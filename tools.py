
import os
from datetime import date
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

def run_query(query, params):
    with sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"]
    ) as connection:

        with connection.cursor() as cursor:
            cursor.execute(query, parameters=params)

            columns = [
                col[0] for col in cursor.description
            ]

            rows = cursor.fetchmany(100)

            return [
                dict(zip(columns, row))
                for row in rows
            ]


def get_network_ratings(network, business_date):
    date.fromisoformat(business_date)

    query = """
    SELECT
        NetworkName,
        ProgramName,
        AirDate,
        SUM(Viewers) AS TotalViewers
    FROM main.agentic_ai_demo.tv_ratings
    WHERE NetworkName = :network
      AND AirDate BETWEEN
          date_sub(to_date(:business_date), 1)
          AND to_date(:business_date)
    GROUP BY NetworkName, ProgramName, AirDate
    ORDER BY AirDate, ProgramName
    """

    return run_query(query, {
        "network": network,
        "business_date": business_date
    })


def get_etl_audit(network, business_date):
    date.fromisoformat(business_date)

    query = """
    SELECT
        PipelineName,
        NetworkName,
        BusinessDate,
        ExecutionStatus,
        SourceRows,
        TargetRows,
        SourceRows - TargetRows AS RowDifference,
        ErrorMessage
    FROM main.agentic_ai_demo.etl_audit
    WHERE NetworkName = :network
      AND BusinessDate = to_date(:business_date)
    """

    return run_query(query, {
        "network": network,
        "business_date": business_date
    })
