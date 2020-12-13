import pandas as pd
import pymysql
from tqdm import tqdm


def import_to_db(input_file):
    df = pd.read_csv(input_file)
    df = df[df["fb_id"] != "not found"]

    conn = pymysql.connect(
        host="94.130.179.7", user="dropship_dev", password="b2HYz9w9gPsKi28", db="dropship_dev"
    )
    cur = conn.cursor()
    i = 1
    for store_domain, facebook_page_url, fb_id in tqdm(
        list(zip(df["url"].values, df["fb"].values, df["fb_id"].values))
    ):
        i += 1
        sqlCmd = "update facebook set store_domain = %s, facebook_page_url = %s where facebook_id like %s"
        cur.execute(sqlCmd, (store_domain, facebook_page_url, f"{fb_id}_%"))
        if i % 10000 == 0:
            conn.commit()

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    import_to_db("out.csv")
