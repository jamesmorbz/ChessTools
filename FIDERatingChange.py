import math

rating_start = 2457
rating_opponent = 2307

while True:
    
    rating_change = (350 - (rating_start - rating_opponent)) // 25

    if rating_change == 0:
        break

    rating_start += rating_change
    rating_opponent -= rating_change

print(rating_start)