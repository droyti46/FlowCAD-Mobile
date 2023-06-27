import cv2
import numpy as np
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarCloseButton
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from ar import ArProcedure

KV = '''
<NumberButton@MagicBehavior+MDIconButton>:
    md_bg_color: '#2DD7AB'

<InstructionScan@MDSwiperItem>:
    title: 'Заголовок'
    desc: 'Описание'
    icon: 'Иконка'

    RelativeLayout:

        MDBoxLayout:
            orientation: 'vertical'
            spacing: '12dp'

            NumberButton:
                id: num_icon
                icon: root.icon
                user_font_size: '56sp'
                opposite_colors: True

            MDLabel:
                id: title_instruction
                font_style: 'H5'
                text: root.title

            MDLabel:
                id: text_instruction
                text: root.desc

MDScreenManager:

    MDScreen:
        name: 'main_menu'
        orientation: 'vertical'
        md_bg_color:  '#1F222B'

        MDBoxLayout:
            orientation: 'vertical'
            spacing: '40dp'

            MDLabel:
                text: 'Опробуйте свое спроектированное здание в дополненной реальности!'
                halign: 'center'
                icon: 'android'

            MDFillRoundFlatIconButton:
                text: 'Отсканировать QR код'
                icon: 'qrcode'
                md_bg_color: '#2DD7AB'
                pos_hint: {'center_x': .5, 'center_y': .5}
                on_release: root.current = 'scanning_qrcode'

            MDBoxLayout:
                md_bg_color: '#3C404C'
                MDSwiper:
                    size_hint_y: None
                    height: 270
                    on_swipe: self.get_current_item().ids.num_icon.shake()

                    InstructionScan:
                        title: 'Скачайте программу'
                        desc: 'Скачайте и загрузите программу для Windows по ссылке из презентации (Она есть в Приложении).'
                        icon: 'numeric-1'

                    InstructionScan:
                        title: 'Сделайте чертеж'
                        desc: 'Запустите программу, создайте в ней новый проект или выберите один из примеров. Постройте чертеж, используя инструменты.'
                        icon: 'numeric-2'

                    InstructionScan:
                        title: 'Сгенерируйте QR код'
                        desc: 'В верхнем меню выберите пункт "AUTO Humour Mobile" и перейдите в "Опробовать в AR".'
                        icon: 'numeric-3'

                    InstructionScan:
                        title: 'Отсканируйте QR код'
                        desc: 'В мобильном приложении нажмите кнопку "Отсканировать QR код" и отсканирйте код, появившийся на экране.'
                        icon: 'numeric-4'

                    InstructionScan:
                        title: 'Готово'
                        desc: 'Теперь вы можете посмотреть на свой проект в дополненной реальности! Остались вопросы? Можно найти ответ в документации!'
                        icon: 'numeric-5'


    MDScreen:
        name: 'scanning_qrcode'
        orientation: 'vertical'
        on_pre_enter: app.start_scanning_qrcode()
        on_leave: app.stop_scanning_qrcode()
        md_bg_color:  '#1F222B'

        MDBoxLayout:
            orientation: 'vertical'

            MDTopAppBar:
                title: 'Сканирование QR кода'
                md_bg_color:  '#2DD7AB'
                anchor_title: 'left'

                left_action_items:
                    [
                    ['arrow-left', lambda x: app.change_screen('main_menu')]
                    ]

            RelativeLayout:

                Camera:
                    id: camera
                    play: True

                Image:
                    source: 'data/images/frame_scanning.png'

                MDFloatingActionButton:
                    icon: 'flashlight'
                    pos_hint: {'center_x': .5, 'center_y': .2}
                    md_bg_color:  '#2DD7AB'

                MDLabel:
                    text: 'Поместите QR код в окошко'
                    halign: 'center'
                    pos_hint: {'center_y': .95}

    MDScreen:
        name: 'qrcode_success'
        orientation: 'vertical'
        on_enter: app.qrcode_success_enter()
        md_bg_color:  '#1F222B'

        MDBoxLayout:
            orientation: 'vertical'

            MDTopAppBar:
                title: 'Сканирование завершено'
                md_bg_color:  '#2DD7AB'
                anchor_title: 'left'

                left_action_items:
                    [
                    ['arrow-left', lambda x: app.change_screen('scanning_qrcode')]
                    ]

            MDLabel:
                text: 'QR код успешно отсканирован!'
                halign: 'center'
                font_style: 'H5'
                theme_text_color: 'Custom'
                text_color: '#2DD7AB'

            MDLabel:
                id: info_about_model
                text: 'Контент'
                halign: 'center'

            MDFillRoundFlatIconButton:
                text: 'Запустить в AR'
                icon: 'cube-scan'
                md_bg_color:  '#2DD7AB'
                pos_hint: {'center_x': .5}
                on_release: root.current = 'ar'

    MDScreen:
        name: 'ar'
        orientation: 'vertical'
        md_bg_color:  '#1F222B'
        on_pre_enter:
            about_ar_sheet.open()
            app.start_show_ar()

        on_leave: app.stop_show_ar()

        MDBoxLayout:
            orientation: 'vertical'

            MDTopAppBar:
                title: 'Просмотр в AR'
                md_bg_color:  '#2DD7AB'
                anchor_title: 'left'

                left_action_items:
                    [
                    ['arrow-left', lambda x: app.change_screen('qrcode_success')]
                    ]

            MDBottomNavigation:
                #panel_color: '#3C404C'
                selected_color_background: '#2DD7AB'
                text_color_active: 'lightgrey'

                MDBottomNavigationItem:
                    name: 'view'
                    text: 'Просмотр'
                    icon: 'cube-scan'

                    Image:
                        id: image_ar

                MDBottomNavigationItem:
                    name: 'param'
                    text: 'Параметры'
                    icon: 'cog'

                    MDSlider
                        hint: True


        MDBottomSheet:
            id: about_ar_sheet
            bg_color: '#3C404C'
            type: 'standard'
            max_opening_height: root.height
            default_opening_height: self.height
            heigth: self.max_opening_height
            adaptive_height: True

            MDBottomSheetDragHandle:

                MDBottomSheetDragHandleTitle:
                    text: 'Вы находитесь в режиме AR'
                    adaptive_height: True
                    font_style: 'H6'
                    pos_hint: {'center_y': .5}

                MDBottomSheetDragHandleButton:
                    icon: 'close'
                    _no_ripple_effect: True
                    on_release: about_ar_sheet.dismiss()

            MDBottomSheetContent:
                padding: '16dp'

                Image:
                    source: 'data/images/tracker.jpg'

                MDLabel:
                    text: 'Наведите камеру телефона на специальный распечатанный трекер, который будет в папке с приложением, чтобы на нем появилась 3D модель.'
                    halign: 'center'
                    adaptive_height: True

'''

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Green'

        return Builder.load_string(KV)

    def on_start(self):
        self.ar = ArProcedure(
                                path_to_tracker = 'data\\images\\tracker.jpg',
                                model = [[[-3, -3, 0],
                                          [+3, -3, 0],
                                          [+3, +3, 0],
                                          [-3, +3, 0],
                                          [+0, +0, +3]],

                                         [[4, 1, 0],
                                          [4, 2, 1],
                                          [3, 4, 0],
                                          [3, 4, 2],
                                          [3, 2, 1],
                                          [3, 1, 0]]]
                             )
        self.converter = Converter()

    def start_scanning_qrcode(self):
        self.camera = self.root.ids.camera
        self.detected_qrcode = Clock.schedule_interval(self.check_qrcode, 0.1)
    def stop_scanning_qrcode(self):
        self.detected_qrcode.cancel()

    def start_show_ar(self):
        self.generate_ar = Clock.schedule_interval(self.display_ar, 0.1)
    def stop_show_ar(self):
        self.generate_ar.cancel()

    def change_screen(self, screen):
        self.root.current = screen

    def check_qrcode(self, dt):
        # Получаем объект текстуру из камеры
        texture = self.camera.texture

        # Конвертируем текстуру в CV2 Image
        img = self.converter.convert_texture_to_cv2(texture)

        # Создаем детектор QR кода
        detector = cv2.QRCodeDetector()

        # Детектим QR код
        try:
            data, bbox, clear_qrcode = detector.detectAndDecode(img)
            if data:
                self.root.current = 'qrcode_success'
                self.qrcode_success_message = MDSnackbar(
                    MDLabel(
                        text = 'Готово',
                    ),

                    MDSnackbarCloseButton(
                        icon = 'close',
                        theme_text_color = 'Custom',
                        text_color = '#2DD7AB',
                        _no_ripple_effect = True,
                        on_release = self.qrcode_success_message_dismiss,
                    ),
                )
                self.qrcode_success_message.open()
                self.data_model = data
        except:
            pass

    def qrcode_success_enter(self):
        model_info = self.root.ids.info_about_model
        cnt_vertices = len(self.data_model.split('\n'))
        model_info.text = rf'''Информация о 3D модели:

Количество вершин: {cnt_vertices}
'''

    def display_ar(self, dt):
        # Получаем объект текстуру из камеры и конвертируем текстуру в CV2 Image
        cap = self.converter.convert_texture_to_cv2(self.camera.texture)

        # Вычисляем и отображаем, как должна выглядеть модель на снимке
        image_cv2 = self.ar.calculate_and_display(cap = cap)

        # Снова получаем текстуру из CV2 Image
        texture = self.converter.convert_cv2_to_texture(image_cv2)

        # Устанавливаем текстуру для изображения
        self.root.ids.image_ar.texture = texture

    def qrcode_success_message_dismiss(self, *args):
        self.qrcode_success_message.dismiss()

class Converter():

    def convert_texture_to_cv2(self, texture):
        # Преобразуем текстуру в набор байтов RGBA, используя pixels
        texture_bytes = texture.pixels

        # Преобразуем в np.array и обрезаем с помощью reshape
        np_array = np.frombuffer(texture_bytes, np.uint8)
        np_array = np_array.reshape(texture.height, texture.width, 4)

        # Картинка
        img = cv2.cvtColor(np_array, cv2.COLOR_RGBA2BGR)
        return img

    def convert_cv2_to_texture(self, cv2_image):
        # Переворачиваем изображение, потому что оно почему-то выходит перевернутым:)
        # Да, костыли
        cv2_image = cv2.flip(cv2_image, 0)

        # Переводим изображение в формат RGB из BGR
        image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

        # Получаем размеры изображения (высоту и ширину)
        height, width = image_rgb.shape[:2]

        # Создаем объект Kivy Texture с соответствующими размерами
        texture = Texture.create(size=(width, height), colorfmt='rgb')

        # Записываем пиксели изображения в текстуру
        texture.blit_buffer(image_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

        return texture


MainApp().run()