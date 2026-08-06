"""
Court Name Normalization Script
Maps abbreviated court codes to full proper names in pls_caselaws collection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# Comprehensive mapping of abbreviated court names to full names
COURT_NAME_MAP = {
    # Major Courts - already correct or minor fixes
    "Supreme Court": "Supreme Court Of Pakistan",
    "SUPREME-COURT": "Supreme Court Of Pakistan",
    "SC": "Supreme Court Of Pakistan",
    
    "Lahore High Court": "Lahore High Court",
    "LAHORE-HIGH-COURT-LAHORE": "Lahore High Court",
    "Lahore": "Lahore High Court",
    "LHC": "Lahore High Court",
    "C-LAHORE": "Lahore High Court",
    
    "Sindh High Court": "Sindh High Court",
    "KARACHI-HIGH-COURT-SINDH": "Sindh High Court",
    "KAR": "Sindh High Court",
    
    "Peshawar High Court": "Peshawar High Court",
    "PESHAWAR-HIGH-COURT": "Peshawar High Court",
    "PHC": "Peshawar High Court",
    
    "Islamabad High Court": "Islamabad High Court",
    "ISLAMABAD": "Islamabad High Court",
    "IHC": "Islamabad High Court",
    
    "Balochistan High Court": "Balochistan High Court",
    "QUETTA-HIGH-COURT-BALOCHISTAN": "Balochistan High Court",
    "B": "Balochistan High Court",
    
    "High Court AJK": "High Court Azad Kashmir",
    "HIGH-COURT-AZAD-KASHMIR": "High Court Azad Kashmir",
    "HC-A": "High Court Azad Kashmir",
    "HCA": "High Court Azad Kashmir",
    "HCAJKJ": "High Court Azad Kashmir",
    
    "Supreme Court AJK": "Supreme Court Azad Kashmir",
    "SCAJK": "Supreme Court Azad Kashmir",
    "SCAK": "Supreme Court Azad Kashmir",
    "SC-A": "Supreme Court Azad Kashmir",
    "SUPAJK": "Supreme Court Azad Kashmir",
    
    # Federal Courts
    "Federal Shariat Court": "Federal Shariat Court",
    "FEDERAL-SHARIAT-COURT": "Federal Shariat Court",
    "Federal Court": "Federal Court Of Pakistan",
    "FC": "Federal Court Of Pakistan",
    "Federal Services Tribunal": "Federal Service Tribunal",
    "Federal Tax Ombudsman": "Federal Tax Ombudsman Pakistan",
    "FEDERAL-CONSTITUTIONAL-COURT": "Federal Constitutional Court",
    
    # Appellate Tribunals
    "Appellate Tribunal": "Appellate Tribunal",
    "Appellate Tribunal Sindh": "Appellate Tribunal Sindh",
    "Appellate Tribunal Punjab": "Appellate Tribunal Punjab",
    "Appellate Tribunal NWFP": "Appellate Tribunal KPK",
    "Appellate Tribunal Balochistan": "Appellate Tribunal Balochistan",
    "AT-PUNJAB": "Appellate Tribunal Punjab",
    "AT-SINDH": "Appellate Tribunal Sindh",
    "AT-A": "Appellate Tribunal Azad Kashmir",
    "AT-BALOCHISTAN": "Appellate Tribunal Balochistan",
    
    # Income Tax Tribunals
    "Income Tax Tribunal": "Income Tax Appellate Tribunal",
    "IT-K": "Income Tax Appellate Tribunal Karachi",
    "IT-L": "Income Tax Appellate Tribunal Lahore",
    "IT-P": "Income Tax Appellate Tribunal Peshawar",
    "IT-DHAKA": "Income Tax Appellate Tribunal Dhaka",
    "IT-BANG": "Income Tax Appellate Tribunal Bangladesh",
    "ITL": "Income Tax Appellate Tribunal Lahore",
    "ITN": "Income Tax Appellate Tribunal",
    "ITM": "Income Tax Appellate Tribunal Multan",
    "ITA": "Income Tax Appellate Tribunal",
    "ITNE": "Income Tax Appellate Tribunal",
    
    # Inland Revenue
    "Inland Revenue Appellate Tribunal": "Appellate Tribunal Inland Revenue",
    "IRAL": "Appellate Tribunal Inland Revenue Lahore",
    
    # Service Tribunals
    "Service Tribunal Punjab": "Service Tribunal Punjab",
    "Service Tribunal Sindh": "Service Tribunal Sindh",
    "Service Tribunal NWFP": "Service Tribunal KPK",
    "Service Tribunal Appellate": "Service Tribunal Appellate",
    "Service Tribunal": "Service Tribunal",
    "ST-BALOCHISTAN": "Service Tribunal Balochistan",
    "ST-BALOSHISTAN": "Service Tribunal Balochistan",
    "ST-PUNJAAB": "Service Tribunal Punjab",
    "PST": "Service Tribunal Punjab",
    "SST": "Service Tribunal Sindh",
    "BST": "Service Tribunal Balochistan",
    "NST": "Service Tribunal KPK",
    "STAJK": "Service Tribunal Azad Kashmir",
    
    # Subordinate Judiciary Service Tribunals
    "PSJST": "Punjab Subordinate Judiciary Service Tribunal",
    "SJST": "Sindh Subordinate Judiciary Service Tribunal",
    "SSJST": "Sindh Subordinate Judiciary Service Tribunal",
    "STSJ": "Subordinate Judiciary Service Tribunal",
    "KPST": "Khyber Pakhtunkhwa Service Tribunal",
    "KPSJ": "KPK Subordinate Judiciary Service Tribunal",
    "KPKSJST": "KPK Subordinate Judiciary Service Tribunal",
    "SJSTKP": "KPK Subordinate Judiciary Service Tribunal",
    "AJKSJST": "AJK Subordinate Judiciary Service Tribunal",
    
    # Labour Courts
    "Labour Court Punjab": "Labour Court Punjab",
    "Labour Court Sindh": "Labour Court Sindh",
    "LC-NWFP": "Labour Court KPK",
    "LC-WP": "Labour Court West Pakistan",
    "LC-BALOCHISTAN": "Labour Court Balochistan",
    "LC-PESHAWAR": "Labour Court Peshawar",
    "LCP": "Labour Court Punjab",
    
    # Labour Appellate Tribunals
    "PLAT": "Labour Appellate Tribunal Punjab",
    "SLAT": "Labour Appellate Tribunal Sindh",
    "BLAT": "Labour Appellate Tribunal Balochistan",
    "LAT-PUNAB": "Labour Appellate Tribunal Punjab",
    "LAT-WP": "Labour Appellate Tribunal West Pakistan",
    "LAT-A": "Labour Appellate Tribunal Azad Kashmir",
    "LAT-PESHAWAR": "Labour Appellate Tribunal Peshawar",
    "LATAJK": "Labour Appellate Tribunal Azad Kashmir",
    "LATQ": "Labour Appellate Tribunal Quetta",
    "PLT": "Punjab Labour Appellate Tribunal",
    
    # Election Tribunals
    "ET-PUNJAB": "Election Tribunal Punjab",
    "ET-SINDH": "Election Tribunal Sindh",
    "ET-NWFP": "Election Tribunal KPK",
    "ET-BALOCHISTAN": "Election Tribunal Balochistan",
    "ET": "Election Tribunal",
    "ETP": "Election Tribunal Punjab",
    "ETL": "Election Tribunal Lahore",
    "ETS": "Election Tribunal Sindh",
    "ETB": "Election Tribunal Balochistan",
    "ETQ": "Election Tribunal Quetta",
    "ETAJK": "Election Tribunal Azad Kashmir",
    "PET": "Pakistan Election Tribunal",
    "ECP": "Election Commission Of Pakistan",
    
    # NIRC / SECP / CCP
    "NIRC": "National Industrial Relations Commission",
    "SECP": "Securities And Exchange Commission Of Pakistan",
    "CCP": "Competition Commission Of Pakistan",
    "CLA": "Corporate Law Authority",
    "SEC": "Securities And Exchange Commission Of Pakistan",
    
    # Customs / Tax Courts
    "CEST": "Customs Excise And Sales Tax Appellate Tribunal",
    "CST": "Customs And Sales Tax Appellate Tribunal",
    "IAT-WP": "Income Tax Appellate Tribunal West Pakistan",
    
    # Banking Courts
    "Banking Court West Pakistan": "Banking Court West Pakistan",
    "Banking Court Punjab": "Banking Court Punjab",
    "BC-NWFP": "Banking Court KPK",
    "BC-PUNJAB": "Banking Court Punjab",
    "BC-SINDH": "Banking Court Sindh",
    "BCQ": "Banking Court Quetta",
    
    # Board of Revenue
    "Revenue Division Punjab": "Board Of Revenue Punjab",
    "BR-SINDH": "Board Of Revenue Sindh",
    "BR-P": "Board Of Revenue Punjab",
    "BRP": "Board Of Revenue Punjab",
    "BR-S": "Board Of Revenue Sindh",
    "BRS": "Board Of Revenue Sindh",
    "BR-NWFP": "Board Of Revenue KPK",
    "BR-B": "Board Of Revenue Balochistan",
    
    # Special Courts
    "Special Appellate Court": "Special Appellate Court",
    "SPECIAL": "Special Court",
    
    # District / Civil Courts
    "District Court Karachi": "District Court Karachi",
    "Civil Court": "Civil Court",
    "DC": "District Court",
    
    # Gilgit-Baltistan
    "Gilgit-Baltistan": "Gilgit Baltistan Chief Court",
    "GBSAC": "Gilgit Baltistan Supreme Appellate Court",
    "SACGB": "Gilgit Baltistan Supreme Appellate Court",
    "GBSC": "Gilgit Baltistan Chief Court",
    "SACG": "Gilgit Baltistan Supreme Appellate Court",
    
    # Supreme Appellate
    "SA": "Supreme Appellate Court",
    "SAJ": "Supreme Appellate Court",
    "SAC-SINDH": "Supreme Appellate Court Sindh",
    "SABAJK": "Shariat Appellate Bench AJK",
    "SAB": "Shariat Appellate Bench",
    "SHAK": "Shariat Court Azad Kashmir",
    
    # NWFP / KPK
    "NWFP Court": "KPK Court",
    "NWFP": "KPK",
    "KPBCT": "KPK Bar Council Tribunal",
    "KEPT": "KPK Environmental Tribunal",
    
    # Historical
    "WPHC": "West Pakistan High Court",
    "WPIC": "West Pakistan Industrial Court",
    "WP-KARACHI": "West Pakistan High Court Karachi",
    "EPHC": "East Pakistan High Court",
    "EPIC": "East Pakistan Industrial Court",
    "EP-LC": "East Pakistan Labour Court",
    
    # International
    "Privy Council": "Privy Council",
    "Supreme Court (India)": "Supreme Court Of India",
    "High Court (India)": "High Court Of India",
    "Appellate Court (India)": "Appellate Court India",
    "Bombay High Court (India)": "Bombay High Court India",
    "K-INDIA": "Karnataka High Court India",
    "C-INDIA": "Calcutta High Court India",
    "MP-INDIA": "Madhya Pradesh High Court India",
    "PH-INDIA": "Punjab And Haryana High Court India",
    "G-INDIA": "Gujarat High Court India",
    "AP-INDIA": "Andhra Pradesh High Court India",
    "D-INDIA": "Delhi High Court India",
    "R-INDIA": "Rajasthan High Court India",
    "PT-INDIA": "Patna High Court India",
    "GH-INDIA": "Gauhati High Court India",
    "HP-INDIA": "Himachal Pradesh High Court India",
    "AN-INDIA": "Andhra Pradesh High Court India",
    "CG-INDIA": "Chhattisgarh High Court India",
    "H-INDIA": "Hyderabad High Court India",
    "MY-INDIA": "Mysore High Court India",
    "O-INDIA": "Orissa High Court India",
    "MR-INDIA": "Maharashtra High Court India",
    "AS-INDIA": "Assam High Court India",
    "HY-INDIA": "Hyderabad High Court India",
    "JK-INDIA": "Jammu And Kashmir High Court India",
    "DIC-INDAI": "Delhi Industrial Court India",
    "NITB-INDIA": "National Industrial Tribunal India",
    "Karachi (India)": "Karachi High Court (India)",
    "SCC": "Supreme Court Of Canada",
    "SCUK": "Supreme Court Of UK",
    "SCUS": "Supreme Court Of The United States",
    "SCNZ": "Supreme Court Of New Zealand",
    "S-CYPRUS": "Supreme Court Of Cyprus",
    "S-USA": "Supreme Court Of The United States",
    "CCSA": "Constitutional Court Of South Africa",
    "SCI": "Supreme Court Of India",
    "SC-L": "Supreme Court Of Sri Lanka",
    "SC-K": "Supreme Court Of Kenya",
    "SC-Q": "Supreme Court Of Qatar",
    "S-BANG": "Supreme Court Of Bangladesh",
    "CA": "Court Of Appeal",
    "HL": "House Of Lords",
    "CD": "Chancery Division",
    "QAT": "Qatar Courts",
    "HC-DHAKA": "High Court Dhaka",
    
    # Ombudsman / Misc
    "POS": "Provincial Ombudsman Sindh",
    "EOB": "Employees Old Age Benefits Institution",
    "ESSI-PUNJAB": "Employees Social Security Institutions Punjab",
    "PBC": "Pakistan Bar Council",
    "SBC": "Sindh Bar Council",
    "PCIC": "Pakistan Criminal Investigation Court",
    "PCIC-K": "Criminal Investigation Court Karachi",
    "PIC-K": "Pakistan Investigation Court Karachi",
    "PKIC": "Pakistan Investigation Court",
    "ISB": "Islamabad",
    "ISC": "Insurance Court",
    "IC": "Industrial Court",
    "IPT": "Intellectual Property Tribunal",
    "IPTSB": "Intellectual Property Tribunal Sindh And Balochistan",
    "PIIT": "Pakistan Insurance Tribunal",
    "ILC": "International Law Court",
    "GLC": "Gilgit Law Court",
    "SJC": "Supreme Judicial Council",
    "CBR": "Central Board Of Revenue",
    "FLC": "Federal Land Commission",
    "ADAT": "Anti Dumping Appellate Tribunal",
    "PRAT": "Punjab Revenue Authority Tribunal",
    "ATPRA": "Appellate Tribunal Punjab Revenue Authority",
    "SRB": "Sindh Revenue Board",
    "CAT": "Competition Appellate Tribunal",
    "NACC": "National Accountability Court",
    "AA": "Arbitrator Award",
    "BAT": "Before Arbitral Tribunal",
    "APW": "Authority Under Payment Of Wages Act",
    "CWC": "Commissioner Workmens Compensation",
    "CEP-SINDH": "Custodian Evacuee Property Sindh",
    "CEP-LAHORE": "Custodian Evacuee Property Lahore",
    "NAS": "Northern Areas Supreme Court",
    "FB-L": "Full Bench Lahore",
    "SEPT": "Service Tribunal Punjab",
    "PSJ": "Punjab Subordinate Judiciary",
    "LOPHC": "Lahore High Court Original Side",
    "IATP": "Income Tax Appellate Tribunal Pakistan",
    "AAR": "Authority For Advance Rulings",
    "NET": "National Environmental Tribunal",
    "SSC-SINDH": "Social Security Court Sindh",
    "SA-P": "Supreme Appellate Court Punjab",
    "BT-NWFP": "Banking Tribunal KPK",
    "ASG": "Additional Sessions Court Gilgit",
    "P-HN": "Peshawar High Court Nowshera",
    "SB": "Shariat Bench",
    "BJ": "Baghdad Ul Jadid",
    "BLT": "Banking Law Tribunal",
    "JC-PESHAWAR": "Judicial Commissioner Court Peshawar",
    "JC-BALOCHISTAN": "Judicial Commissioner Court Balochistan",
    "I-PUNJAB": "Insurance Tribunal Punjab",
    "IS": "Insurance Court Sindh",
    "ISB": "Islamabad",
    "Multan Bench": "Lahore High Court Multan Bench",
    "Rawalpindi Bench": "Lahore High Court Rawalpindi Bench",
    "H": "Hyderabad Bench",
    "E": "Environment Court",
    "J": "Judicial Commissioner Court",
    "SC-Q": "Supreme Court Qatar",
    "STS": "Service Tribunal Sindh",
    "STB": "Service Tribunal Balochistan",
    "HC": "High Court",
}


async def normalize_courts():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    total_updated = 0
    for old_name, new_name in COURT_NAME_MAP.items():
        if old_name == new_name:
            continue
        result = await db.pls_caselaws.update_many(
            {"court": old_name},
            {"$set": {"court": new_name}}
        )
        if result.modified_count > 0:
            print(f"  Updated {result.modified_count:,} cases: '{old_name}' -> '{new_name}'")
            total_updated += result.modified_count
    
    # Handle null courts
    null_result = await db.pls_caselaws.update_many(
        {"court": None},
        {"$set": {"court": "Unknown Court"}}
    )
    if null_result.modified_count > 0:
        print(f"  Updated {null_result.modified_count:,} null courts -> 'Unknown Court'")
        total_updated += null_result.modified_count
    
    print(f"\nTotal cases updated: {total_updated:,}")
    
    # Print new court distribution
    cursor = db.pls_caselaws.aggregate([
        {"$group": {"_id": "$court", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 30}
    ])
    courts = await cursor.to_list(30)
    print("\nTop 30 courts after normalization:")
    for c in courts:
        print(f"  {c['count']:>6,} | {c['_id']}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(normalize_courts())
