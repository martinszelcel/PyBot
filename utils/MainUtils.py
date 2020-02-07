
def get_number_emoji(number, medals=False):
    emojis = [':zero:',':one:', ':two:', ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]
    medal_emojis = [':first_place:', ':second_place:', ":third_place:"]
    if number <= 3 and medals:
        result = medal_emojis[number - 1]
    elif number > 10:
        number = str(number)
        result = ""
        for digit in number:
            result += emojis[int(digit)]
    else:
        result = emojis[number]
    return result
