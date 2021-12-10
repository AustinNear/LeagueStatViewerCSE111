def int_safe(num, default=0):
    try:
        return int(num)
    except:
        return default

champ_types_dict = {
    "Top": "Top",
    "Jungle": "Jungle",
    "Middle": "Middle",
    "ADC": "ADC",
    "Support": "Support",
}