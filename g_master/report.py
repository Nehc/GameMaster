from reportlab.lib.pagesizes import portrait, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image #, Spacer
from reportlab.lib.styles import ParagraphStyle #, getSampleStyleSheet 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Arial','arial.ttf', 'UTF-8'))

def create_pdf(file_name, world_description, hero_name, 
               hero_characteristics, hero_description, summa,
               world_image, hero_image, translator,
               GM_ans=[], pl_act=[],scene_ls = [],scene_img=[],
               ):
    '''
    create PDF-file with your story to send it to friends or print
    '''
    # Создаем документ
    doc = SimpleDocTemplate(file_name, pagesize=portrait(A4))
    story = []

    # Добавляем картинку мира
    story.append(Image(f'./images/{world_image}', 640/2, 480/2))

    # Добавляем описание мира
    world_style = ParagraphStyle('world_style')
    world_style.alignment = 1
    world_style.fontSize = 12
    world_style.spaceAfter = 10
    world_style.spaceBefore = 10
    story.append(Paragraph(f'<font name="Arial">{world_description}</font>', world_style))

    # Добавляем досье главного героя
    hero_style = ParagraphStyle('hero_style')
    hero_style.alignment = 1
    hero_style.fontSize = 18
    hero_style.spaceAfter = 20
    hero_style.spaceBefore = 20
    story.append(Paragraph('<font name="Arial">Досье главного героя</font>', hero_style))

    # Добавляем имя героя
    hero_name_style = ParagraphStyle('hero_name_style')
    hero_name_style.fontSize = 14
    hero_name_style.spaceAfter = 10
    hero_name_style.spaceBefore = 10
    story.append(Paragraph(f'<font name="Arial">Имя: {hero_name}</font>', hero_name_style))

    # Добавляем фото героя
    story.append(Image(f'./images/{hero_image}', 300/2, 300/2, hAlign='RIGHT'))

    # Добавляем характеристики героя
    hero_characteristics_style = ParagraphStyle('hero_characteristics_style')
    hero_characteristics_style.fontSize = 12
    hero_characteristics_style.spaceAfter = 10
    hero_characteristics_style.spaceBefore = 10
    story.append(Paragraph(f'<font name="Arial">{hero_characteristics}</font>', hero_characteristics_style))

    # Добавляем описание
    description_style = ParagraphStyle('description_style')
    description_style.fontSize = 12
    description_style.spaceAfter = 10
    description_style.spaceBefore = 10

    story.append(Paragraph(f'<font name="Arial">{hero_description}</font>', description_style))

    story.append(Paragraph('<font name="Arial">Впред к приключениям!</font>', hero_style))

    j = 0; k = 0; scene = True
    for i in range(len(GM_ans)):
        if GM_ans[i]==scene_ls[k]:
            scene = True
        if scene:
            story.append(Image(f'./images/{scene_img[k]}', 640/2, 480/2))
            #story.append(Paragraph(f'<font name="Arial"><b>Img:</b>{scene_img[j]}</font>', description_style))
            if len(scene_ls)>k+1:
                k+=1
            story.append(Paragraph(f'<font name="Arial"><b>GAME MASTER: </b>{translator.translate(GM_ans[i],dest="ru").text}</font>', description_style))
            scene = False
        else:
            if len(pl_act)>j:
                story.append(Paragraph(f'<font name="Arial"><b>PLAYER: </b>{translator.translate(pl_act[j],dest="ru").text}</font>', description_style))
                j+=1
            story.append(Paragraph(f'<font name="Arial"><b>GAME MASTER: </b>{translator.translate(GM_ans[i],dest="ru").text}</font>', description_style))

    #story.append(Paragraph(f'<font name="Arial">TL;DR</font>', hero_name_style))

    #story.append(Paragraph(f'<font name="Arial">{translator.translate(summa,dest="ru").text}</font>', description_style))

    story.append(Paragraph('<font name="Arial">The END?</font>', hero_style))

    # Генерируем документ
    doc.build(story)
