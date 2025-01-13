# UniMIB-ResearchGraph

The project involves creating a graph database that maps authors from the Department of Computer Science at the University of Milano-Bicocca, following all steps of data management, from acquisition to integration and quality assessment. It helps analyze research trends, key contributors, and collaborations, while also exploring the department's global impact through external partnerships. Students can use it to understand research areas, topics, and collaborations within the department and with international universities. o optimize user interaction, a chatbot powered by Gemini was developed using Graph RAG, leveraging the LangGraph library.


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

## Data acquisition and cleaning

*Note*: the execution time is not optimal and it may take a lot of time

Execute the code in this order:
1. Authors internal of Bicocca: Run retrieve_bicocca_authors.py
2. Clean internal authors: Run clean_scraping_Dataset.py
3. Get orcid of internal authors: Run retrieve_metadata_internal.py
4. Get all metadata with gscholar for internal authors: Run retrieve_citations_gscholar.py
5. Get past institutions of internal authors: Run retrieve_past_institutions.py
6. Get all written papers after 2018: Run the file inside data_acquisition directory retrieve_papers.py
7. Clean papers: Run notebook clean_papers.ipynb
8. Authors external of Bicocca: Run retrieve_metadata_external.py
9. Retrieve meta data of external authors: Go to retrieve_citations_gscholar.py and modified datasetpath with the created dataset of the previous point and run the retrieve_citations_gscholar.py
10. Retrieve all institutions: Run retrieve_institutions.py
11. Retrieve institutions id: inside authors/data_acquisition Run retrieve_institutionsId.py
12. Merge internal and external authors: Run merge_datasets.py
13. Clean all authors: Run clean_authors.py
14. Retrieve all topics: after processing the papers now retrieve all the topics running the topics.py inside Topics folder

## Data Storage and Integration

Execute the code in this order inside the Data Storage directory of GraphDB:
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

## Graphrag and chatbot

Execute the code in this order inside the Chatbot directory:
1. Install the plugin APOC inside neo4j
2. `app.py`: Run this file to execute the chatbot

## Fast execution

Copy the file from the data processed directory and paste it into the import directory
of neo4j and follow the procedure from Data storage and Integration
