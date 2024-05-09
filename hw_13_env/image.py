from PIL import Image, ImageDraw

# Створення нового зображення
width, height = 200, 200
image = Image.new('RGB', (width, height), (255, 255, 255))

# Додавання тексту на зображення
draw = ImageDraw.Draw(image)
draw.text((10, 10), "Test Image", fill=(0, 0, 0))

# Збереження зображення
image.save('src/static/default-avatar.png')
