export const regionOptions = [
    "ar", "at", "au", "be", "br", "ca", "ch", "cl", "cn", "co", "cz", "de", 
    "dk", "ee", "eg", "es", "fi", "fr", "gb", "gr", "hk", "hu", "id", "ie", 
    "il", "in", "is", "it", "jp", "kr", "kw", "lk", "lt", "lv", "mx", "my", 
    "nl", "no", "nz", "pe", "ph", "pk", "pl", "pt", "qa", "ro", "ru", "sa", 
    "se", "sg", "sr", "sw", "th", "tr", "tw", "us", "ve", "vn", "za"
]

export const exchangeOptions = {
    ar: ["BUE."], at: ["VIE."], au: ["ASX."], be: ["BRU"],
    br: ["SAO."], ca: ["CNQ", "NEO", "TOR", "VAN"], ch: ["EBS."], cl: ["SGO."],
    cn: ["SHH", "SHZ"], co: ["BVC."], cz: ["PRA"], de: ["BER", "DUS", "FRA", "GER", "HAM", "MUN", "STU"],
    dk: ["CPH."], ee: ["TAL."], eg: ["CAI."], es: ["MCE"], fi: ["HEL."], fr: ["PAR."],
    gb: ["AQS", "IOB", "LSE"], gr: ["ATH."], hk: ["HKG."], hu: ["BUD."], id: ["JKT"],
    ie: ["ISE."], il: ["TLV."], in: ["BSE", "NSI"], is: ["ICE."], it: ["MIL."],
    jp: ["FKA", "JPX", "SAP"], kr: ["KOE", "KSC."], kw: ["KUW."], lk: [], lt: ["LIT."],
    lv: ["RIS."], mx: ["MEX."], my: ["KLS"], nl: ["AMS."], no: ["OSL."], nz: ["NZE."],
    pe: [], ph: ["PHP", "PHS."], pk: [], pl: ["WSE"], pt: ["LIS."], qa: ["DOH."],
    ro: ["BVB."], ru: [], sa: ["SAU."], se: ["STO."], sg: ["SES."], sr: [], sw: ["EBS."],
    th: ["SET."], tr: ["IST"], tw: ["TAI", "TWO"], 
    us: ["ASE", "BTS", "CXI", "NCM", "NGM", "NMS", "NYQ", "OEM", "OQB", "OQX", "PCX", "PNK", "YHD"],
    ve: ["CCS."], vn: [], za: ["JNB"],
}

export const sectorOptions = [
  "Basic Materials",
  "Communication Services",
  "Consumer Cyclical",
  "Consumer Defensive",
  "Energy",
  "Financial Services",
  "Healthcare",
  "Industrials",
  "Real Estate",
  "Technology",
  "Utilities"
];


export const industryOptions = {
    "Basic Materials": [
        "Agricultural Inputs", "Aluminum", "Building Materials", "Chemicals", "Coking Coal", 
        "Copper", "Gold", "Lumber & Wood Production", "Other Industrial Metals & Mining", 
        "Other Precious Metals & Mining", "Paper & Paper Products", "Silver", "Specialty Chemicals", "Steel"
    ],
    "Communication Services": [
        "Advertising Agencies", "Broadcasting", "Electronic Gaming & Multimedia", "Entertainment", 
        "Internet Content & Information", "Publishing", "Telecom Services"
    ],
    "Consumer Cyclical": [
        "Apparel Manufacturing", "Apparel Retail", "Auto & Truck Dealerships", "Auto Manufacturers", 
        "Auto Parts", "Department Stores", "Footwear & Accessories", "Furnishings, Fixtures & Appliances", 
        "Gambling", "Home Improvement Retail", "Internet Retail", "Leisure", "Lodging", "Luxury Goods", 
        "Packaging & Containers", "Personal Services", "Recreational Vehicles", "Residential Construction", 
        "Resorts & Casinos", "Restaurants", "Specialty Retail", "Textile Manufacturing", "Travel Services"
    ],
    "Consumer Defensive": [
        "Beverages - Brewers", "Beverages - Non-Alcoholic", "Beverages - Wineries & Distilleries", 
        "Confectioners", "Discount Stores", "Education & Training Services", "Farm Products", 
        "Food Distribution", "Grocery Stores", "Household & Personal Products", "Packaged Foods", "Tobacco"
    ],
    "Energy": [
        "Oil Gas Drilling", "Oil Gas E P", "Oil Gas Equipment Services", "Oil Gas Integrated", 
        "Oil Gas Midstream", "Oil Gas Refining Marketing", "Thermal Coal", "Uranium"
    ],
    "Financial Services": [
        "Asset Management", "Banks Diversified", "Banks Regional", "Capital Markets", "Credit Services", 
        "Financial Conglomerates", "Financial Data Stock Exchanges", "Insurance Brokers", "Insurance Diversified", 
        "Insurance Life", "Insurance Property Casualty", "Insurance Reinsurance", "Insurance Specialty", 
        "Mortgage Finance", "Shell Companies"
    ],
    "Healthcare": [
        "Biotechnology", "Diagnostics Research", "Drug Manufacturers General", 
        "Drug Manufacturers Specialty Generic", "Health Information Services", "Healthcare Plans", 
        "Medical Care Facilities", "Medical Devices", "Medical Distribution", 
        "Medical Instruments Supplies", "Pharmaceutical Retailers"
    ],
    "Industrials": [
        "Aerospace Defense", "Airlines", "Airports Air Services", "Building Products Equipment", 
        "Business Equipment Supplies", "Conglomerates", "Consulting Services", "Electrical Equipment Parts", 
        "Engineering Construction", "Farm Heavy Construction Machinery", "Industrial Distribution", 
        "Infrastructure Operations", "Integrated Freight Logistics", "Marine Shipping", "Metal Fabrication", 
        "Pollution Treatment Controls", "Railroads", "Rental Leasing Services", "Security Protection Services", 
        "Specialty Business Services", "Specialty Industrial Machinery", "Staffing Employment Services", 
        "Tools Accessories", "Trucking", "Waste Management"
    ],
    "Real Estate": [
        "Real Estate Development", "Real Estate Diversified", "Real Estate Services", "Reit Diversified", 
        "Reit Healthcare Facilities", "Reit Hotel Motel", "Reit Industrial", "Reit Mortgage", 
        "Reit Office", "Reit Residential", "Reit Retail", "Reit Specialty"
    ],
    "Technology": [
        "Communication Equipment", "Computer Hardware", "Consumer Electronics", "Electronic Components", 
        "Electronics Computer Distribution", "Information Technology Services", "Scientific Technical Instruments", 
        "Semiconductor Equipment Materials", "Semiconductors", "Software Application", "Software Infrastructure", "Solar"
    ],
    "Utilities": [
        "Utilities Diversified", "Utilities Independent Power Producers", "Utilities Regulated Electric", 
        "Utilities Regulated Gas", "Utilities Regulated Water", "Utilities Renewable"
    ]
}