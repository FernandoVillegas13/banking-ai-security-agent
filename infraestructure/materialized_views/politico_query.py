import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL")
schema = os.getenv("SCHEMA")

def create_deepfeel_materialized_view_politico(analysis_id, table_name: str):

    create_view_sql = f"""
    CREATE MATERIALIZED VIEW IF NOT EXISTS {schema}.{table_name} AS
    SELECT
        e.comment_id,
        to_timestamp(d."date", 'DD/MM/YY HH24:MI:SS')::date AS date,
        e.metadata->>'NPS' AS nps,
        (e.metadata->>'concern')::numeric(5,2) AS concern,
        (e.metadata->>'empathy')::numeric(5,2) AS empathy,
        (e.metadata->>'neutral')::numeric(5,2) AS neutral,
        (e.metadata->>'approval')::numeric(5,2) AS approval,
        (e.metadata->>'optimism')::numeric(5,2) AS optimism,
        (e.metadata->>'surprise')::numeric(5,2) AS surprise,
        (e.metadata->>'annoyance')::numeric(5,2) AS annoyance,
        (e.metadata->>'admiration')::numeric(5,2) AS admiration,
        (e.metadata->>'excitement')::numeric(5,2) AS excitement,
        (e.metadata->>'disapproval')::numeric(5,2) AS disapproval,
        e.metadata->>'motivo_descripcion_corta' AS motivo,
        e.metadata->>'conclusion_descripcion_corta' AS conclusion,
        e.metadata->>'referencia_descripcion_corta' AS referencia,
        e.metadata->>'intencion_de_voto_descripcion_corta' AS intencion_de_voto,
        e.metadata->>'tipo_de_comentario_descripcion_corta' AS tipo_de_comentario,
        e.metadata->>'genero_usuario_descripcion_corta' AS genero,
        e.metadata->>'rango_etario_estimado_descripcion_corta' AS rango_etario_estimado,
        e.metadata->>'nivel_de_polarizacion_descripcion_corta' AS nivel_de_polarizacion,
        e.metadata->>'elementos_persuasivos_descripcion_corta' AS elementos_persuasivos,
        e.metadata->>'sectores_prioritarios_descripcion_corta' AS sectores_prioritarios,
        e.metadata->>'identificacion_valores_descripcion_corta' AS identificacion_valores,
        e.metadata->>'percepcion_de_credibilidad_descripcion_corta' AS percepcion_de_credibilidad
        FROM {schema}.analysis a
        LEFT JOIN 
            {schema}.analysis_export_comments b
            ON b.analysis_id = a.id 
        LEFT JOIN 
            {schema}.export_comment_job c
            ON c.id = b.export_comments_id
        LEFT JOIN
            {schema}.extracted_comments d
            ON d.job_id  = c.id
        inner join
        	{schema}.analyzed_comments e
        	on e.comment_id = d.id 
        WHERE a.guid = '{analysis_id}';
    """
    
    create_indexes_sql = [
        f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{schema}_comment_id ON {schema}.{table_name}(comment_id);"
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_date ON {schema}.{table_name}(date);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_date_desc ON {schema}.{table_name}(date DESC);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_referencia ON {schema}.{table_name}(referencia);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_nps ON {schema}.{table_name}(nps);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_tipo_comentario ON {schema}.{table_name}(tipo_de_comentario);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_intencion_voto ON {schema}.{table_name}(intencion_de_voto);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_genero ON {schema}.{table_name}(genero);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_nivel_polarizacion ON {schema}.{table_name}(nivel_de_polarizacion);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_date_referencia ON {schema}.{table_name}(date, referencia);",
        f"CREATE INDEX IF NOT EXISTS idx_{schema}_referencia_nps ON {schema}.{table_name}(referencia, nps);",
    ]
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Verificar si existe
            check_exists = text(f"""
                SELECT EXISTS (
                    SELECT FROM pg_matviews 
                    WHERE schemaname = '{schema}' AND matviewname = '{table_name}'
                );
            """)
            
            result = conn.execute(check_exists)
            exists = result.scalar()
            
            if exists:
                conn.execute(text(f"DROP MATERIALIZED VIEW {schema}.{table_name} CASCADE;"))
                conn.commit()
            
            # Crear vista
            conn.execute(text(create_view_sql))
            conn.commit()
            print("Vista materializada creada exitosamente.")
            
            # Crear índices
            for idx, index_sql in enumerate(create_indexes_sql, 1):
                conn.execute(text(index_sql))
                print(f"   [{idx}/{len(create_indexes_sql)}] Índice creado")
            conn.commit()
            print("Todos los índices creados exitosamente.")            
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise