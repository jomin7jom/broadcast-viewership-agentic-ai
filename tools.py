
import os
from datetime import date
from dotenv import load_dotenv
from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal

load_dotenv()

# Databricks connection settings
hostname = os.environ["DATABRICKS_SERVER_HOSTNAME"]
http_path = os.environ["DATABRICKS_HTTP_PATH"]

# OAuth machine-to-machine authentication
config = Config(
    host=f"https://{hostname}",
    client_id=os.environ["DATABRICKS_CLIENT_ID"],
    client_secret=os.environ["DATABRICKS_CLIENT_SECRET"],
    auth_type="oauth-m2m",
    token=None,
)

def credential_provider():
    return oauth_service_principal(config)


def run_query(query, params):
    with sql.connect(
        server_hostname=hostname,
        http_path=http_path,
        credentials_provider=credential_provider
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
