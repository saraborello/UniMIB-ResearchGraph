# Citation-network

<img width="950" alt="Graph" src="https://github.com/user-attachments/assets/37233051-fd95-4020-b327-a489d282f20d">

## Structure

The project is structured as follows:

- `data`: contains the extracted data organized in two directories:
    - `processed`: final integreted data used to populate the graph database
    - `raw`: extracted data from different sources which necessed integration and cleaning

- `src`: contains all the python code:
    - `Authors`: all the code for the authors node organized in the two phases of data acquisition and cleaning
    - `Institutions`: all the code for the Institutions node organized in the two phases of data acquisition and cleaning
    - `GraphDB`: all the code for creating the graph, testing its quality and the queries for answering the research questions and comunity detection
    - `Papers`: all the code for the Papers node organized in the two phases of data acquisition and cleaning
    - `Topics`: all the code for the Topics node organized in the two phases of data acquisition and cleaning

## Setup
To set up the project, you need to install the required dependencies listed in the `environment.yml` file. You can do this by running the following command in your terminal:

```bash
conda env create -f environment.yml
```
Once the environment is created, activate it by running:

```bash
conda activate citation_network
```

### Environment Variables

To configure the project, you need to create a `.env` file in the root directory of the project. Create a new file named `.env` and define the following variables:

- **`PYTHONPATH`**: This variable defines the root directory of the project. Set it to the path where your project is located.

- **`BASE_DIR`**: This variable represents the base directory of the project. Set it to the path where your project is stored.

- **`GEMINI_KEY`**: This is the API key for accessing the Gemini API.

## Data acquisition

*Note*: the execution time is not optimal and it may take a lot of time

Execute the code in this order:
1. Authors:
2. Institutions:
3. Papers: Run the file inside data_acquisition directory

## Data Cleaning

Execute the code in this order:
1. Authors:
2. Papers: Run the file inside data_acquisition directory of papers
3. Topics: after processing the papers now retrieve all the topics running the `topics.py` inside the Topics directory

## Data Storage and Integration

Execute the code in this order inside the Data Storage directory:
1. Copy the created final dataset of the four nodes inside the import directory of neo4j graph database
2. `createDB.py`: run this file to create the graph database, authors and papers nodes make sure to set correctly the variables inside this file
3. `create_topic_node.py`: Run this file to create the topic nodes
4. `create_institutions_node.py`: Run this file to create the institutions nodes

## Data Quality

Execute the code in this order inside the Data Quality directory:
1. `Completeness.py`: Run this file to test the completeness make sure to set correctly the variables inside this file
2. `Consistency.py`: Run this file to test the consistency make sure to set correctly the variables inside this file

## Data Querying

Execute the code in this order inside the Data Querying directory:
1. `neo4j_research_queries.py`: Run this file to run the cypher queries
2. `comunity_detection.cypher`: Run this file to perform the comunity detection also copying, pasting into Neo4j