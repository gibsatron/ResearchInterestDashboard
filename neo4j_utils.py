from neo4j import GraphDatabase

URI = "neo4j://localhost"
AUTH = ("neo4j", "ilovecs411")  # Replace with your actual password

def run_query(query, parameters=None, database="academicworld"):
    # Create a driver instance
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    # Verify connectivity and run query
    try:
        with driver.session(database=database) as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
    except Exception as e:
        print(f"Query failed: {e}")
    finally:
        driver.close()

