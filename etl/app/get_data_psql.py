import datetime
import json
import logging
import psycopg2

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from psycopg2.extensions import connection as _connection

import my_connection
from state_redis import RedisStorage, State

BULK = 1000


def create_tables_list():
    tables_list = list()
    tables_list.append('movies')
    tables_list.append('genres')
    tables_list.append('persons')

    return tables_list


def check_state(table_name, state):
    current_state = state.get_state('modified_'+table_name)
    if current_state is None:
        current_state = datetime.datetime.min
        state.set_state('modified_'+table_name, current_state.isoformat())
    return current_state


def get_data_from_table(pg_conn: _connection, table: str, redis_state: State):

    try:
        with pg_conn.cursor() as p_curs:

            modified = check_state(table, redis_state)

            if table == 'movies':
                query_text = """
                SELECT json_agg(movies_data)
                FROM (
                    SELECT
                        fw.id as _id,
                        fw.id,
                        fw.title,
                        fw.description,
                        fw.rating as imdb_rating,
                        COALESCE(
                            json_agg(
                                DISTINCT p.full_name
                                ) FILTER (WHERE pfw.role = 'director'),
                            '[]')
                        as director,
                        COALESCE (
                            json_agg(
                                DISTINCT jsonb_build_object(
                               'id', p.id,
                               'name', p.full_name
                                )
                            ) FILTER (WHERE p.id is not null AND pfw.role = 'actor'),
                            '[]'
                        ) as actors,
                        COALESCE (
                            json_agg(
                                DISTINCT p.full_name
                                ) FILTER (WHERE p.id is not null AND pfw.role = 'actor'),
                            '[]'
                        ) as actors_names,
                        COALESCE (
                            json_agg(
                                DISTINCT jsonb_build_object(
                               'id', p.id,
                               'name', p.full_name
                                )
                            ) FILTER (WHERE p.id is not null AND pfw.role = 'writer'),
                            '[]'
                        ) as writers,
                        COALESCE (
                            json_agg(
                                DISTINCT p.full_name
                                ) FILTER (WHERE p.id is not null AND pfw.role = 'writer'),
                            '[]'
                        ) as writers_names,
                        array_agg(DISTINCT g.name) as genre
                    FROM content.film_work fw
                    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                    LEFT JOIN content.person p ON p.id = pfw.person_id
                    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                    LEFT JOIN content.genre g ON g.id = gfw.genre_id
                    WHERE fw.updated_at > %s         
                    GROUP BY fw.id
                    ORDER BY fw.updated_at) 
                movies_data;"""

            elif table == 'genres':
                query_text = """
                                SELECT json_agg(genre_data)
                                FROM (
                                    SELECT
                                        g.id as _id,
                                        g.id,
                                        g.name
                                        
                                    FROM content.genre g) 
                                genre_data;"""

            elif table == 'persons':
                query_text = """
                SELECT json_agg(persons_data)
                FROM (
                     SELECT
                         p.id as _id,
                         p.id,
                         p.full_name
                     FROM content.person p
                     WHERE p.updated_at > %s        
                     ORDER BY p.updated_at) 
                persons_data;"""

            p_curs.execute(query_text, (modified,))
            data = p_curs.fetchall()
            f_name = table + '.json'
            with open(f_name, 'w') as f_data:
                json.dump(data[0][0], f_data)

            send_data_to_es(table, redis_state)

    except psycopg2.Error as error:
        logging.error('Ошибка чтения таблицы ', table, error)


def send_data_to_es(index_name, state):
    es_client = my_connection.connect_to_esl()
    if es_client.ping():
        index_created = create_index(es_client, index_name)
        if index_created:
            try:
                file_name = index_name + '.json'
                with open(file_name, 'r') as data:
                    bulk_data = json.load(data)
                response = helpers.bulk(es_client, bulk_data, index=index_name)
                logging.info(' '.join(('Bulk', str(response[0]), 'documents')))
                state.set_state('modified_'+index_name, datetime.datetime.now().isoformat())
            except Exception as e:
                logging.error(e.args[0])


def create_index(es_object: Elasticsearch, index_name: str):
    created = False
    fname = "index_settings_"+index_name+".json"
    with open(fname, 'r') as ind_set:
        settings = json.load(ind_set)
    try:
        if not es_object.indices.exists(index=index_name):
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            logging.info(' '.join(('Created Index', index_name)))
        created = True
    except Exception as ex:
        logging.error(ex)
    finally:
        return created


def load_from_psql(pg_conn: _connection):
    state = my_connection.connect_to_redis()
    tables_list = create_tables_list()
    for table_name in tables_list:
        get_data_from_table(pg_conn, table_name, state)


if __name__ == '__main__':
    while True:
        my_connection.connect_to_db()
