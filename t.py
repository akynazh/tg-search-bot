def test(page):
    stars = list(range(20))
    stars_tmp = [None] * 80
    stars = stars_tmp[:((page - 1) * 20)] + stars + stars_tmp[((page - 1) * 20):]
    return stars
res = test(5)
print(res)
print(len(res))