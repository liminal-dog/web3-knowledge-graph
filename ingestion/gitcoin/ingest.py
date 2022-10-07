from ..helpers import Ingestor
from .cyphers import GitCoinCyphers

class GitCoinIngestor(Ingestor):
    def __init__(self):
        self.cyphers = GitCoinCyphers()
        super().__init__("gitcoin")

    def ingest_grants(self):
        "This function ingests the grant data loaded in the self.data"
        grants_data = self.process_grants_data()
        
        urls = self.s3.save_json_as_csv(
            grants_data["grants"], self.bucket_name, f"ingestor_grants_{self.asOf}")
        self.cyphers.create_or_merge_grants(urls)

        urls = self.s3.save_json_as_csv(
            grants_data["team_members"], self.bucket_name, f"ingestor_team_members_{self.asOf}")
        self.cyphers.create_or_merge_team_members(urls)
        self.cyphers.link_or_merge_team_members(urls)

        urls = self.s3.save_json_as_csv(
            grants_data["admin_wallets"], self.bucket_name, f"ingestor_admins_{self.asOf}")
        self.cyphers.create_or_merge_admins(urls)
        self.cyphers.link_or_merge_admin_wallet(urls)

        urls = self.s3.save_json_as_csv(
            grants_data["twitter_accounts"], self.bucket_name, f"ingestor_twitter_{self.asOf}")
        self.cyphers.create_or_merge_twitter_accounts(urls)
        self.cyphers.link_or_merge_twitter_accounts(urls)

    def process_grants_data(self):
        grants_data = {
            "grants": [],
            "team_members": [],
            "admin_wallets": [],
            "twitter_accounts": [],
        }
        for grant in self.scraper_data["grants"]:
            tmp = {
                "id": grant["id"],
                "title": grant["title"],  
                "text": grant["description"].replace('"', ""),  
                "types": [el["fields"]["name"] for el in grant["grant_type"]],  
                "tags": [el["fields"]["name"] for el in grant["grant_tags"]],
                "url": f"https://gitcoin.co/{grant['url']}",
                "amount": grant["amount_received"],
                "amountDenomination": "USD",
                "asOf": self.asOf
            }
            grants_data["grants"].append(tmp)
            
            tmp = {
                "grantId": grant["id"],
                "address": grant["admin_address"].lower()
                }
            grants_data["admin_wallets"].append(tmp)

            for member in grant["team_members"]:
                tmp = {
                    "grantId": grant["id"],
                    "userId": member["pk"],
                    "handle": member["fields"]["handle"]
                }
                grants_data["team_members"].append(tmp)
            if grant["twitter_handle_1"]:
                tmp = {
                    "grantId": grant["id"],
                    "handle": grant["twitter_handle_1"]
                }
                grants_data["twitter_accounts"].append(tmp)
                if grant["twitter_handle_1"] != grant["twitter_handle_2"] and grant["twitter_handle_2"]:
                    tmp = {
                        "grantId": grant["id"],
                        "handle": grant["twitter_handle_2"]
                    }
                    grants_data["twitter_accounts"].append(tmp)
        return grants_data

    def ingest_donations(self):
        "This function ingests the donnations loaded in the self.data"
        donations_data = self.process_donations()
        urls = self.s3.save_json_as_csv(
            donations_data, self.bucket_name, f"ingestor_donations_{self.asOf}")
        self.cyphers.create_or_merge_donators(urls)
        self.cyphers.link_or_merge_donations(urls)

    def process_donations(self):
        donations_data = []
        for donation in self.scraper_data["donations"]:
            tmp = {
                "token": donation["token"].lower(),
                "amount": donation["amount"],
                "donor": donation["donor"].lower(),
                "destination": donation["dest"].lower(),
                "txHash": donation["txHash"].lower(),
                "chain": donation["chain"],
                "chainId": donation["chainId"]
            }
            donations_data.append(tmp)
        return donations_data

    def ingest_bounties(self):
        "This function ingests the bounties loaded in the self.data"
        bounties_data = self.process_bounty_data()

        urls = self.s3.save_json_as_csv(
            bounties_data["bounties"], self.bucket_name, f"ingestor_bounties_{self.asOf}")
        self.cyphers.create_or_merge_bounties(urls)

        urls = self.s3.save_json_as_csv(
            bounties_data["bounties_owners"], self.bucket_name, f"ingestor_bounties_owners_{self.asOf}")
        self.cyphers.create_or_merge_bounties_owners(urls)
        self.cyphers.link_or_merge_bounties_owners(urls)

        urls = self.s3.save_json_as_csv(
            bounties_data["bounties_owners_addresses"], self.bucket_name, f"ingestor_bounties_owners_{self.asOf}")
        self.cyphers.create_or_merge_bounty_owner_wallets(urls)
        self.cyphers.link_or_merge_bounty_owner_wallets(urls)

        urls = self.s3.save_json_as_csv(
            bounties_data["bounties_fullfilments"], self.bucket_name, f"ingestor_bounties_fullfilments_{self.asOf}")
        self.cyphers.create_or_merge_bounties_fullfilers(urls)
        self.cyphers.link_or_merge_bounties_fullfilers(urls)

        urls = self.s3.save_json_as_csv(
            bounties_data["bounties_fullfilments_addresses"], self.bucket_name, f"ingestor_bounties_fullfilments_{self.asOf}")
        self.cyphers.create_or_merge_bounties_fullfilers_wallets(urls)
        self.cyphers.link_or_merge_bounties_fullfilers_wallets(urls)

        urls = self.s3.save_json_as_csv(
            bounties_data["bounties_interests"], self.bucket_name, f"ingestor_bounties_interests_{self.asOf}")
        self.cyphers.create_or_merge_bounties_interested(urls)
        self.cyphers.link_or_merge_bounties_interested(urls)
        
    def process_bounty_data(self):
        bounties_data = {
            "bounties": [],
            "bounties_owners": [],
            "bounties_owners_addresses": [],
            "bounties_interests": [],
            "bounties_fullfilments": [],
            "bounties_fullfilments_addresses": [],
        }
        for bounty in self.scraper_data["bounties"]:
            tmp = {
                "id": bounty["pk"],
                "title": bounty["title"].replace('"', '').replace("'", ""),
                "text": bounty["issue_description_text"].replace('"','').replace("'", ""),
                "url": bounty["url"].replace('"', '').replace("'", ""),
                "github_url": bounty["github_url"].replace('"', '').replace("'", ""),
                "status": bounty["status"],
                "value_in_token": bounty["value_in_token"],
                "token_name": bounty["token_name"],
                "token_address": bounty["token_address"].lower(),
                "bounty_type": bounty["bounty_type"],
                "project_length": bounty["project_length"],
                "experience_level": bounty["experience_level"],
                "keywords": bounty["keywords"].replace('"', '').replace("'", ""),
                "token_value_in_usdt": bounty["token_value_in_usdt"],
                "network": bounty["network"],
                "org_name": bounty["org_name"].replace('"', '').replace("'", ""),
                "asOf": self.asOf
            }
            bounties_data["bounties"].append(tmp)

            if bounty["bounty_owner_profile"]:
                tmp = {
                    "bounty_id": bounty["pk"], 
                    "id": bounty["bounty_owner_profile"]["id"], 
                    "handle": bounty["bounty_owner_profile"]["handle"], 
                    "name": bounty["bounty_owner_name"], 
                    "keywords": ", ".join(bounty["bounty_owner_profile"]["keywords"]),
                    "email": bounty["bounty_owner_email"],
                    "asOf": self.asOf
                }
                bounties_data["bounties_owners"].append(tmp)

            if bounty["bounty_owner_address"] and bounty["bounty_owner_profile"]:
                tmp = {
                    "id": bounty["bounty_owner_profile"]["id"],
                    "address": bounty["bounty_owner_address"].lower(), 
                    "asOf": self.asOf
                }
                bounties_data["bounties_owners_addresses"].append(tmp)


            for fulfilment in bounty["fulfillments"]:
                if fulfilment["profile"]:
                    tmp = {
                        "bounty_id": bounty["pk"],
                        "email": fulfilment["fulfiller_metadata"]["notificationEmail"] if "notificationEmail" in fulfilment["fulfiller_metadata"] else "Anonymous",
                        "accepted": fulfilment["accepted"],
                        "id": fulfilment["profile"]["id"],
                        "name": fulfilment["profile"]["name"],
                        "handle": fulfilment["profile"]["handle"],
                        "keywords": ", ".join(fulfilment["profile"]["keywords"]),
                        "asOf": self.asOf,
                        "organizations": ", ".join([key for key in fulfilment["profile"]["organizations"]])
                    }
                    bounties_data["bounties_fullfilments"].append(tmp)

                    if fulfilment["fulfiller_address"]:
                        tmp = {
                            "id": fulfilment["profile"]["id"],
                            "address": fulfilment["fulfiller_address"].lower(),
                            "asOf": self.asOf,
                        }
                        bounties_data["bounties_fullfilments_addresses"].append(tmp)

            for interest in bounty["interested"]:
                tmp = {
                    "bounty_id": bounty["pk"],
                    "id": interest["profile"]["id"],
                    "name": interest["profile"]["name"],
                    "handle": interest["profile"]["handle"],
                    "keywords": ", ".join(interest["profile"]["keywords"]),
                    "organizations": ", ".join([key for key in interest["profile"]["organizations"]])
                }
                bounties_data["bounties_interests"].append(tmp)
        return bounties_data

    def run(self):
        self.ingest_grants()
        self.ingest_donations()
        self.ingest_bounties()

if __name__ == "__main__":
    ingestor = GitCoinIngestor()
    ingestor.run()