from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
from flask import session
from src.utils.db import connect

def add_reference(user_id, ref_id, ref_name, columns, values):
    con = connect()
    cur = con.cursor()

    cur.execute(generate_add_sql(columns), (user_id, ref_id, ref_name) + tuple(values))

    con.commit()
    con.close()

def generate_add_sql(columns):
    column = ", ".join(columns)
    formatter = ", ".join("%s" for _ in range(len(columns)))
    return f"INSERT INTO tblReference (user_id, reference_id, reference_name, {column}) VALUES (%s, %s, %s, {formatter})"

def get_references(user_id):

    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM tblReference WHERE user_id=%s", (user_id,))

    filtered_results = []
    results = _get_keys_and_values(cur)
    for dict in results:
        new_dict = {}
        for (key, value) in dict.items():
            if value and not None:
                new_dict[key] = value
        filtered_results.append(new_dict)
    con.close()

    print(generate_bibtex_string(filtered_results))
    return filtered_results

def generate_bibtex_string(entries):
    new_entries = []
    skip = ['id', 'user_id']
    for dict in entries:
        bib_dict = {}
        for (key, value) in dict.items():
            if key == 'reference_name':
                bib_dict['ENTRYTYPE'] = value.lower()
                continue
            if key == 'reference_id':
                bib_dict['ID'] = value
                continue
            if key in skip:
                continue
            else:
                bib_dict[key] = value
        new_entries.append(bib_dict)
                
    db = BibDatabase()
    db.entries = new_entries
    
    writer = BibTexWriter()
    with open('bibtex.bib', 'w+') as bibfile:
        bibfile.write(writer.write(db))
        bibfile.seek(0,0)
        return bibfile.read().splitlines()

def _get_keys_and_values(cursor):
    rows = cursor.fetchall()
    keys = [k[0] for k in cursor.description]
    return [dict(zip(keys, row)) for row in rows]
