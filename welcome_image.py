from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import requests
from io import BytesIO
import math

def create_circle_mask(size):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    return mask

def download_font(url, save_path):
    if not os.path.exists(save_path):
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)
    return save_path

def create_welcome_image(member_name="", avatar_url=None, output_path="welcome.png"):
    # إنشاء صورة جديدة بخلفية سوداء
    width = 1024
    height = 500
    image = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(image)

    # إضافة تأثير التدرج للخلفية
    for y in range(height):
        r = int(41 * (1 - y/height))
        g = int(71 * (1 - y/height))
        b = int(91 * (1 - y/height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # تحميل الخطوط
    font_url = "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
    font_path = "Poppins-Bold.ttf"
    try:
        font_path = download_font(font_url, font_path)
        welcome_font = ImageFont.truetype(font_path, 90)
        name_font = ImageFont.truetype(font_path, 60)
    except:
        welcome_font = ImageFont.load_default()
        name_font = ImageFont.load_default()

    # إضافة دائرة خلفية للصورة الشخصية
    circle_center = (width // 2, 160)
    circle_radius = 80
    draw.ellipse(
        (circle_center[0] - circle_radius - 3,
         circle_center[1] - circle_radius - 3,
         circle_center[0] + circle_radius + 3,
         circle_center[1] + circle_radius + 3),
        fill='white'
    )

    # إضافة الصورة الشخصية
    if avatar_url:
        try:
            # تحميل وتحضير الصورة الشخصية
            response = requests.get(avatar_url)
            avatar = Image.open(BytesIO(response.content))
            avatar = avatar.convert('RGB')
            
            # تحجيم الصورة
            avatar = avatar.resize((circle_radius * 2, circle_radius * 2))
            
            # إنشاء قناع دائري
            mask = create_circle_mask((circle_radius * 2, circle_radius * 2))
            
            # تطبيق القناع
            output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            # لصق الصورة في المركز
            image.paste(
                avatar,
                (circle_center[0] - circle_radius,
                 circle_center[1] - circle_radius),
                mask
            )
        except Exception as e:
            print(f"Error loading avatar: {str(e)}")
            # رسم دائرة رمادية كمكان للصورة
            draw.ellipse(
                (circle_center[0] - circle_radius,
                 circle_center[1] - circle_radius,
                 circle_center[0] + circle_radius,
                 circle_center[1] + circle_radius),
                fill='#2f3136'
            )
    else:
        # رسم دائرة رمادية كمكان للصورة
        draw.ellipse(
            (circle_center[0] - circle_radius,
             circle_center[1] - circle_radius,
             circle_center[0] + circle_radius,
             circle_center[1] + circle_radius),
            fill='#2f3136'
        )

    # إضافة نص الترحيب
    welcome_text = "WELCOME"
    bbox = draw.textbbox((0, 0), welcome_text, font=welcome_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 280),
        welcome_text,
        fill='white',
        font=welcome_font
    )

    # إضافة اسم العضو
    bbox = draw.textbbox((0, 0), member_name, font=name_font)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 370),
        member_name,
        fill='#5865f2',  # لون Discord
        font=name_font
    )

    # إضافة زخرفة
    decoration_color = '#5865f2'
    line_length = 200
    line_y = 340
    center_x = width // 2
    
    # خط مع نقطة في النهاية (يسار)
    draw.line(
        [(center_x - 20, line_y), (center_x - line_length, line_y)],
        fill=decoration_color,
        width=2
    )
    draw.ellipse(
        (center_x - line_length - 5, line_y - 5,
         center_x - line_length + 5, line_y + 5),
        fill=decoration_color
    )
    
    # خط مع نقطة في النهاية (يمين)
    draw.line(
        [(center_x + 20, line_y), (center_x + line_length, line_y)],
        fill=decoration_color,
        width=2
    )
    draw.ellipse(
        (center_x + line_length - 5, line_y - 5,
         center_x + line_length + 5, line_y + 5),
        fill=decoration_color
    )

    # حفظ الصورة
    image.save(output_path)
    return output_path

if __name__ == "__main__":
    # إنشاء صورة تجريبية
    # يمكنك تجربة رابط صورة شخصية حقيقي هنا
    avatar_url = None  # "https://example.com/avatar.png"
    create_welcome_image()
    print("Welcome image has been created!")
