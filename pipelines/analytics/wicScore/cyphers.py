from tqdm import tqdm
from ...helpers import Cypher
from ...helpers import get_query_logging, count_query_logging
from ...helpers import Queries

class WICScoreAnalyticsCyphers(Cypher):
    def __init__(self, database=None):
        super().__init__(database)
        self.queries = Queries()

    def create_constraints(self):
        pass

    def create_indexes(self):
        pass

    @get_query_logging
    def get_positive_WIC_degrees(self, negative_labels):
        query = f"""
            MATCH (w:Wallet)-[:_HAS_CONTEXT]-(wic:_Wic)
            WHERE NOT wic:{"|".join(negative_labels)}
            RETURN distinct(w.address) as address, apoc.node.degree(w, "_HAS_CONTEXT") as deg
        """
        result = self.query(query)
        return result

    @get_query_logging
    def get_negative_WIC_degrees(self, negative_labels):
        query = f"""
            MATCH (w:Wallet)-[:_HAS_CONTEXT]-(wic:_Wic)
            WHERE wic:{"|".join(negative_labels)}
            RETURN distinct(w.address) as address, apoc.node.degree(w, "_HAS_CONTEXT") as deg
        """
        result = self.query(query)
        return result

    @count_query_logging
    def save_reputation_score(self, data):
        count = 0
        query = """
            UNWIND $data as data
            MATCH (wallet:Wallet {address: data.address})
            SET wallet.positiveReputationScore = data.positiveReputationScore
            SET wallet.negativeReputationScore = data.negativeReputationScore
            SET wallet.lastScoreComputeDt = datetime()
            RETURN count(wallet)
        """
        for batch in tqdm(range(0, len(data), 10000), desc="Saving the scores ..."):
            count += self.query(query, {"data": data[batch:batch+10000]})[0].value()
        return count
