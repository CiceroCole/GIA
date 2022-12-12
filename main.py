from PIL import Image
from json import load
import tkinter
from os import listdir
from os.path import dirname, join, basename
from random import randint
from tkinter.messagebox import askokcancel
from tkinter.filedialog import asksaveasfilename, askopenfilename
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from datetime import datetime
from sys import exit


class Get_Img_API:
    def __init__(self, master: tkinter.Tk):
        self.master = master
        with open('./data.json') as jf:
            ljf = load(jf)
            self.urls: list = ljf['urls']
            self.request_datas: list = ljf['request_datas']
            self.support_type: list = ljf["support_type"]
            print(['support_type :', self.support_type])
        self.urls_len = len(self.urls)
        self.url = self.urls[0]
        self.now_img_url = ''
        self.request_data: dict = self.request_datas[0]
        # self.url = 'http://127.0.0.1:5050/Img_Test'
        self.temp_file_path = './temp.png'
        self.img_mode = Image.NEAREST
        self.now_file_path = './temp.png'
        self.now_file_dir = './'
        self.now_file_dir_list = []
        self.now_url_index: int = 0
        self.now_file_dir_list_len: int = int()
        # self.switch = 'random'
        self.switch = 'order'
        self.acquired_mode = 'web'
        self.switch_interval = 30
        self.have_set_up_win = False
        self.img_width, self.img_height = None, None
        self.the_img: Image.Image = Image.Image()
        self.screen_size = self.get_screen_size()
        print('Screen size:', self.screen_size)

        self.get_save_img(url_=self.url, save_path=self.temp_file_path)
        img = tkinter.PhotoImage(file='temp.png')
        self.the_img_weg = tkinter.Label(master=self.master, image=img)
        self.the_img_weg.pack()

        self.auto_switch()
        self.the_img_weg.bind('<Button-1>', lambda _: self.configure_image(self.the_img_weg))
        self.the_img_weg.bind('<Button-2>', lambda _: self.set_up() if not self.have_set_up_win else None)
        self.the_img_weg.bind('<Button-3>', lambda _: self.save_img())
        self.master.bind('<Escape>', lambda _: self.master.quit())

    @staticmethod
    def is_int(var):
        try:
            int(var)
            return True
        except ValueError:
            return False

    def auto_switch(self):
        if self.switch_interval != 'STOP':
            self.configure_image(self.the_img_weg)
            self.master.after(ms=self.switch_interval * 1000, func=self.auto_switch)

    def run(self):
        self.master.update()
        self.master.mainloop()

    def data_refresh(self):
        with open('./data.json') as jf:
            ljf = load(jf)
            self.urls: list = ljf['urls']
            self.request_datas: list = ljf['request_datas']
            self.support_type: list = ljf["support_type"]
            print(['support_type :', self.support_type])
        self.urls_len = len(self.urls)

    @staticmethod
    def get_screen_size():
        tk = tkinter.Tk()
        width = tk.winfo_screenwidth()
        height = tk.winfo_screenheight()
        tk.quit()
        tk.destroy()
        return width, height

    def get_adaptive_screen_image(self, url_: str = None, path: str = None, request_data_: dict = None):
        img_f, image = None, None
        if url_ is not None:
            try:
                img_f = urlopen(url_, data=request_data_)
            except HTTPError:
                print('网络或服务器请求错误!')
                input('输入回车键退出 :')
                exit(0)
            except URLError:
                print('网络或服务器链接错误! error_code: {}'.format(img_f.getcode()))
                input('输入回车键退出 :')
                exit(0)
            self.now_img_url = img_f.geturl()
            image = Image.open(fp=img_f)
        elif path is not None:
            img_f = open(path, 'rb')
            image = Image.open(fp=img_f)
        else:
            print('没有输入文件路径!')
            input('输入回车键退出 :')
            exit(0)

        def convert_h_w(h=None, w=None):
            if h is not None:
                base_height_ = self.screen_size[1] - 10
                h_percent_ = base_height_ / float(image_size[1])
                w_size_ = int(float(image_size[0]) * float(h_percent_))
                h_size_ = base_height_
                return w_size_, h_size_
            if w is not None:
                base_width_ = self.screen_size[0] - 10
                w_percent_ = base_width_ / float(image_size[0])
                h_size_ = int(float(image_size[1]) * float(w_percent_))
                w_size_ = base_width_
                return w_size_, h_size_

        image_size = image.size
        w_size, h_size = convert_h_w(w=image_size[0])
        if h_size > self.screen_size[1]:
            w_size, h_size = convert_h_w(h=image_size[1])
        self.img_width, self.img_height = w_size, h_size

        # 重新设置大小
        # 默认情况下，PIL使用Image.NEAREST过滤器进行大小调整，从而获得良好的性能，但质量很差。
        # image = image.resize((w_size, h_size), Image.ANTIALIAS)
        image = image.resize((w_size, h_size), resample=self.img_mode)
        print('| Original size: ', image_size)
        print('| Now image size: ', image.size)
        img_f.close()
        return image

    def center_show(self, label: tkinter.Label):
        show_x = self.screen_size[0] // 2 - self.img_width // 2
        show_y = self.screen_size[1] // 2 - self.img_height // 2
        label.pack_forget()
        label.place(x=show_x, y=show_y)
        label.update()

    def configure_image(self, label: tkinter.Label):
        self.get_save_img(url_=self.url, save_path=self.temp_file_path, request_data_=self.request_data)
        img_ = tkinter.PhotoImage(file='temp.png')
        label.config(image=img_)
        self.center_show(label=label)

    def get_save_img(self, url_: str = None, request_data_: dict = None, save_path: str = './temp.png'):
        if self.acquired_mode == 'web':
            self.the_img = self.get_adaptive_screen_image(url_=url_, request_data_=request_data_)
        elif self.acquired_mode == 'local':
            self.the_img = self.get_adaptive_screen_image(path=self.now_file_path)
        self.the_img.save(save_path)
        self.switch_url()

    def save_img(self):
        init_file_name = datetime.now().strftime('%Y-%m-%d$%H_%M_%S.%f') + '.png'
        save_file_path = asksaveasfilename(filetypes=[('PNG', '*.png'), ('JPG', '*.jpg'), ('任意图片格式', '')],
                                           defaultextension='*.png',
                                           initialfile=init_file_name)
        if save_file_path:
            self.the_img.save(fp=save_file_path)

    def set_up(self):
        self.have_set_up_win = True
        post_win = tkinter.Tk()
        post_win.title('设置')
        post_win.geometry('300x250')
        post_win.attributes("-topmost", True)
        post_win.resizable(False, False)
        tkinter.Label(master=post_win, text='设置').pack(pady=10)

        def fast_mode():
            self.img_mode = Image.NEAREST

        def hd_mode():
            self.img_mode = Image.ANTIALIAS

        def local_mode():
            self.acquired_mode = 'local'
            self.now_file_path = askopenfilename(title='请选择图片文件')
            self.now_file_dir = dirname(self.now_file_path)
            now_file_dir_list = listdir(self.now_file_dir)
            for file_name in now_file_dir_list:
                file_name_suffix = file_name.split('.')[-1].upper()
                if file_name_suffix in self.support_type:
                    self.now_file_dir_list.append(file_name)
            self.now_file_dir_list_len = len(self.now_file_dir_list)
            print(['now_file_dir_list :', self.now_file_dir_list])
            print('Now img dir path: ', self.now_file_dir)

        def web_mode():
            self.acquired_mode = 'web'

        def set_random():
            self.switch = 'random'
            order_button.deselect()
            print('switch :', self.switch)

        def set_order():
            self.switch = 'order'
            random_button.deselect()
            print('switch :', self.switch)

        def set_switch_interval():
            ent_switch_interval = switch_interval_ent.get()
            if self.is_int(ent_switch_interval):
                self.switch_interval = int(ent_switch_interval)
                print('图片自动切换时间间隔设置为 %d (秒)' % self.switch_interval)
            elif ent_switch_interval == '':
                self.switch_interval = 30
            else:
                self.switch_interval = 'STOP'

        tkinter.Label(master=post_win, text='图片加载模式').pack()
        check_frame1 = tkinter.Frame(master=post_win)
        tkinter.Button(master=check_frame1, text='快速模式',
                       command=fast_mode).pack(side=tkinter.LEFT, padx=5)
        tkinter.Button(master=check_frame1, text='高清模式',
                       command=hd_mode).pack(side=tkinter.LEFT, padx=5)
        check_frame1.pack()

        tkinter.Label(master=post_win, text='图片获取模式').pack()
        check_frame2 = tkinter.Frame(master=post_win)
        tkinter.Button(master=check_frame2, text='本地模式',
                       command=local_mode).pack(side=tkinter.LEFT, padx=5)
        tkinter.Button(master=check_frame2, text='网络模式',
                       command=web_mode).pack(side=tkinter.LEFT, padx=5)
        check_frame2.pack()
        check_frame3 = tkinter.Frame(master=post_win)
        random_button = tkinter.Checkbutton(master=check_frame3, text='随机模式', command=set_random)
        order_button = tkinter.Checkbutton(master=check_frame3, text='顺序模式', command=set_order)
        random_button.pack(side=tkinter.LEFT, padx=5)
        order_button.pack(side=tkinter.LEFT, padx=5)
        check_frame3.pack()
        tkinter.Button(master=post_win, text='配置数据刷新',
                       command=self.data_refresh).pack(ipadx=5)
        check_frame4 = tkinter.Frame(master=post_win)
        tkinter.Label(master=check_frame4, text='设置切换间隔(s)').pack(side=tkinter.LEFT)
        switch_interval_ent = tkinter.Entry(master=check_frame4, width=6)
        switch_interval_ent.pack(side=tkinter.LEFT)
        tkinter.Button(master=check_frame4, text='确认', command=set_switch_interval, ).pack(side=tkinter.LEFT)
        check_frame4.pack()

        if self.switch == 'order':
            order_button.select()
        else:
            random_button.select()
        switch_interval_ent.delete(0, 'end')
        switch_interval_ent.insert(0, str(self.switch_interval))

        def del_win():
            post_win.quit()
            post_win.destroy()
            self.have_set_up_win = False

        post_win.protocol('WM_DELETE_WINDOW', del_win)
        post_win.mainloop()

    def switch_url(self):
        if self.acquired_mode == 'web':
            if self.switch == 'random':
                random_index = randint(0, self.urls_len - 1)
                self.url = self.urls[random_index]
                self.request_data = self.request_datas[random_index]
            elif self.switch == 'order':
                self.now_url_index = self.now_url_index + 1
                if self.now_url_index == self.urls_len:
                    self.now_url_index = 0
                print('| Now api url :', self.url)
                print('| Now img url :', self.now_img_url)
                print('| Now url index :', self.now_url_index)
                print('——' * 25)
                self.url = self.urls[self.now_url_index]
                self.request_data = self.request_datas[self.now_url_index]
        elif self.acquired_mode == 'local':
            if self.switch == 'random':
                now_files_len = self.now_file_dir_list_len
                now_files_name = self.now_file_dir_list[randint(0, now_files_len - 1)]
                print('| Now file name:', now_files_name)
                self.now_file_path = join(self.now_file_dir, now_files_name)
            elif self.switch == 'order':
                now_file_name = basename(self.now_file_path)
                now_file_index = self.now_file_dir_list.index(now_file_name)
                if now_file_index == len(self.now_file_dir_list):
                    now_file_index = 0
                next_file = self.now_file_dir_list[now_file_index + 1]
                print('| Now file name:', next_file)
                self.now_file_path = join(self.now_file_dir, next_file)
        self.master.update()


if __name__ == '__main__':
    if askokcancel(title='提示', message='左键切换\n中键设置\n右键保存\nEsc退出'):
        root = tkinter.Tk()
        root.title('Get_Img_API')
        win_h_w = 900, 600
        root.geometry('{}x{}'.format(*win_h_w))
        # root.geometry('{}x{}'.format(*root.maxsize()))
        root.attributes('-fullscreen', True)
        # root.attributes("-topmost", 2)
        app = Get_Img_API(root)
        app.run()
