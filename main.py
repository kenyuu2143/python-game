import pygame as pg
from pygame.locals import *
import random


#画面サイズの設定（
WIDTH = 1200
HEIGHT = int(WIDTH * 0.7)

#色の設定
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 20, 40)
YELLOW = (250, 200, 0)
SKYBLUE = (0,50,150)
#フォントの設定
font_name = pg.font.match_font('MSゴシック')

#テキスト描画用の関数（別のゲームなどでも使いまわしできます）
def draw_text(screen,text,size,x,y,color):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface,text_rect)

#バックグラウンドクラス
class Background:
    def __init__(self):
        #画像をロードしてtransformでサイズ調整（画面サイズに合わせる）
        self.image = pg.image.load('png/BG.png').convert_alpha()
        self.image = pg.transform.scale(self.image,(WIDTH,HEIGHT))
        #画面のスクロール設定
        self.scroll = 0
        self.scroll_speed = 4
        self.x = 0
        self.y = 0
        #0と画面横サイズの二つをリストに入れておく
        self.imagesize = [0,WIDTH]

    #描画メソッド
    def draw_BG(self,screen): 
        #for文で２つの位置に１枚づつバックグラウンドを描画する（描画するx位置は上で指定したimagesizeリスト）
        for i in range(2):      
            screen.blit(self.image,(self.scroll + self.imagesize[i], self.y))
        self.scroll -= self.scroll_speed
        #画像が端まで来たら初期位置に戻す
        if abs(self.scroll) > WIDTH:
            self.scroll = 0

#プレイヤークラス
class Plane(pg.sprite.Sprite):
    #インスタンス化時の初期位置を引数x、yに指定
    def __init__(self,x,y):
        #スプライトクラスの初期化
        pg.sprite.Sprite.__init__(self) 
        
        #イメージを空リストに格納していく
        self.idleimgs = []
        for i in range(1,3):
            num = str(i)
            if len(num) == 1:
                num = "0" + num   
            image = pg.image.load(f'png/Plane/{num}.png').convert_alpha()         
            image = pg.transform.scale(image,(95,75))
            self.idleimgs.append(image)        
        
        #弾丸発射時のイメージをリストに格納していく
        self.shotimgs = []
        for i in range(3,8):
            num = str(i)
            if len(num) == 1:
                num = "0" + num   
            image = pg.image.load(f'png/Plane/{num}.png').convert_alpha()         
            image = pg.transform.scale(image,(95,75))
            self.shotimgs.append(image)

        #敵に接触時のイメージをリストに格納していく
        self.deadimgs = []
        self.deadimg = pg.image.load('png/Plane/08.png').convert_alpha()
        #１枚の画像を回転させながら８枚格納
        for i in range(8):
            self.deadimg = pg.transform.scale(self.deadimg,(95,75))
            self.deadimg = pg.transform.rotate(self.deadimg,90 * i)
            self.deadimgs.append(self.deadimg)

        #リスポン時の無敵状態の画像をリストに格納
        self.immortal_imgs = []
        for i in range(9,10):
            num = str(i)
            if len(num) == 1:
                num = "0" + num                  
            image = pg.image.load(f'png/Plane/{num}.png').convert_alpha()         
            image = pg.transform.scale(image,(95,75))
            self.immortal_imgs.append(image)

        #描画する画像を指定するための設定
        self.index = 0
        self.image = self.idleimgs[self.index]

        self.image.set_colorkey(SKYBLUE)
        #画像のrectサイズを取得
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        #radiusは当たり判定の設定に必要
        self.radius = 40
        
        #現在の状態をture,falseで管理
        self.IDLE = True
        self.SHOT = False
        self.DEAD = False
        self.READY = False
        self.IMMORTAL = False

        self.dy = 20
        #無敵時間の設定 
        self.immortal_timer = 60

        #残機イメージの関連（左上に表示される）
        self.plane_mini_img = pg.image.load('png/Plane/01.png').convert_alpha()
        #サイズ調整で小さくする
        self.plane_mini_img = pg.transform.scale(self.plane_mini_img,(50,35))
        self.plane_mini_img.set_colorkey((255,255,255))
        self.lives = 3
    
    #残機描画用メソッド      
    def draw_lives(self,screen,x,y):
        for i in range(self.lives):
            img_rect = self.plane_mini_img.get_rect()
            img_rect.x = x + 55 * i
            img_rect.y = y
            screen.blit(self.plane_mini_img,img_rect)

    #キー操作に合わせて状態が変化するので、その状態に合わせて画像を描画するメソッド
    def change_img(self,imglist):
        self.index += 1
        if self.index >= len(imglist):
            self.index = 0
        self.image = imglist[self.index]
    
    #弾丸発射キーを押した場合に後に作成する弾丸クラスがインスタンス化される
    def create_bullet(self):
        return Bullet(self.rect.center[0] + 20,self.rect.center[1] + 20)

    #毎フレームの処理用メソッド
    def update(self):
        #描画する画像を現在の状態から指定
        if self.IDLE:
            self.change_img(self.idleimgs)
        if self.SHOT:
            self.change_img(self.shotimgs)
        if self.DEAD:
            self.change_img(self.deadimgs)
        if self.immortal_timer < 60:
            self.change_img(self.immortal_imgs)
        
        #キー操作関連
        key = pg.key.get_pressed()
        #墜落している状態で無ければ以下の入力を受け付ける
        if self.DEAD == False:
            #上下左右の移動
            if key[pg.K_a]:
                self.rect.x -= 10
                if self.rect.x <= 0: 
                    self.rect.x = 0 

            if key[pg.K_d]: 
                self.rect.x += 10 
                if self.rect.x >= WIDTH - 75:
                    self.rect.x = WIDTH - 75

            if key[pg.K_w]:
                self.rect.y -= 10
                if self.rect.y <= 0: 
                    self.rect.y = 0 

            if key[pg.K_s]: 
                self.rect.y += 10 
                if self.rect.y >= HEIGHT - 75:
                    self.rect.y = HEIGHT - 75

        #墜落中の場合、斜め下に移動していく
        if self.DEAD:
            self.rect.x += 3
            self.rect.y += 10           

#弾丸クラス                      
class Bullet(pg.sprite.Sprite):
    def __init__(self,x,y):
        #スプライトクラスの初期化
        pg.sprite.Sprite.__init__(self)

        #イメージを空のリストに格納
        self.bullet_images = []
        for i in range(1,6):
            img = pg.image.load(f'png/Bullet/{i}.png').convert_alpha()
            img = pg.transform.scale(img,(30,30))
            self.bullet_images.append(img)
        
         #描画する画像を指定するための設定
        self.index = 0
        self.image = self.bullet_images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]        
        
    #毎フレームの処理用メソッド   
    def update(self):        
        self.rect.x += 40
        #位置が右端までいった場合の処理（killで自分自身をスプライトグループから削除する）
        if self.rect.x >= WIDTH:
            self.kill() 

        #毎フレーム画像を切り替える処理
        self.index += 1
        if self.index >= len(self.bullet_images):
            self.index = 0
        self.image = self.bullet_images[self.index]

#敵キャラ１クラス（ロケットみたいなやつ）
class Mob(pg.sprite.Sprite):
    def __init__(self,x,y) -> None:
        #スプライトクラスの初期化
        pg.sprite.Sprite.__init__(self)
        
        #990 * 640（元の画像サイズ）
        #空のリスト設定
        self.images = []
        #サイズを３種類設定し、ランダムに設定するようにする
        self.imagesize = [(72,46),(144,92),(108,69)]
        random_num = random.choice(self.imagesize)
        #空のリストに画像を格納していく
        for i in range(1,3):
            img = pg.image.load(f'png/frame{i}.png').convert_alpha()
            img = pg.transform.scale(img,random_num)
            img = pg.transform.flip(img,180, 0)
            self.images.append(img)

        #描画する画像を指定するための設定
        self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey(SKYBLUE)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.radius = int(self.rect.x / 2)
        #初期配置をランダムに設定する
        self.dx = random.randint(1,15)
        self.dy = random.randint(-6,6)
        self.dy = 0
    
    #毎フレームの処理用メソッド 
    def update(self):
        self.rect.x -= self.dx
        self.rect.y -= self.dy
        #move範囲
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.dy *= -1 

        if self.rect.right < 0:
            self.rect.x = WIDTH
        #画像インデックス送り
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]  

#敵キャラ2クラス（緑色の爆弾みたいなやつ）
class Mob2(pg.sprite.Sprite):
    def __init__(self,x,y) -> None:
        pg.sprite.Sprite.__init__(self)

        #409 * 522（元画像のサイズ）
        #空のリスト設定
        self.images = []
        #サイズ調整
        sizex = int(409 / 8)
        sizey = int(522 / 8)

        #リストに画像を格納
        for i in range(1,17):
            num = str(i)
            if len(num) == 1:
                num = "0" + num 
            img = pg.image.load(f'png/robotball/{num}.png').convert_alpha()
            img = pg.transform.scale(img,(sizex,sizey))
            self.images.append(img)
        
        #描画する画像を指定するための設定
        self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey(SKYBLUE)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.radius = int(sizex / 2)
        #落下スピード設定
        self.dy = random.randint(8,15)
        #初期位置　Y　をリストで設定しておく
        self.init_Y_position = [-2000,-3000,-4000,-5000,-6000]

    #毎フレームの処理用メソッド    
    def update(self):
        self.rect.y += self.dy
        #描画の範囲
        if self.rect.top > HEIGHT:
            self.rect.y = random.choice(self.init_Y_position)
            self.rect.x = random.randint(200,WIDTH - 100)      

        #画像インデックス送り
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]


#敵キャラ3クラス（ボス登場時に現れる黄色のやつ）
class Minion(pg.sprite.Sprite):
    def __init__(self,x,y) -> None:
        #スプライトクラスの初期化
        pg.sprite.Sprite.__init__(self)

        #817 * 619(元画像のサイズ）
        #空のリスト設定
        self.images = []
        #サイズ調整
        sizeX = int(817 / 10)
        sizeY = int(619 / 10)

        #リストに画像を格納
        for i in range(1,5):
            img = pg.image.load(f'png/minion/{i}.png').convert_alpha()
            img = pg.transform.scale(img,(sizeX,sizeY))
            img = pg.transform.flip(img,180, 0)
            self.images.append(img)

        #描画する画像を指定するための設定
        self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey(SKYBLUE)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.radius = int(sizeX / 2)
        #移動速度
        self.dx = 20
        self.dy = 100
        
    #毎フレームの処理用メソッド 
    def update(self):
        self.rect.x -= self.dx
        if self.rect.x <= -50:
            self.rect.x = WIDTH + 100
            self.rect.y += self.dy
        if self.rect.y >= HEIGHT + 50:
            self.rect.y = 0
                
        #画像インデックス送り
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]     

#UFOのクラス
class UFO(pg.sprite.Sprite):
    def __init__(self,x,y):
        #スプライトクラスの初期化
        pg.sprite.Sprite.__init__(self)

        #1584 * 1071(元画像のサイズ）
        #空のリスト設定
        self.images = []
        #サイズ調整
        sizex = int(1584 / 14)
        sizey = int(1071 / 14)
        #毎フレームの動きの角度範囲を指定
        degree = [0, 5, 10, 15, 20, 15, 10, 5, 0, -5, -10, -15, -20, -15, -10, -5]

        #リストに画像を格納
        for i in range(16):
            img = pg.image.load("png/ufo.png").convert_alpha()
            img = pg.transform.scale(img,(sizex,sizey))
            img = pg.transform.flip(img,180,0)
            img = pg.transform.rotate(img, degree[i])
            self.images.append(img)
        
        #描画する画像を指定するための設定
        self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey(SKYBLUE)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.radius = int(sizex / 2)
        #UFO登場の条件設定
        self.ufo_appear = False
        self.ufo_move = False
        self.ufo_timer = 0
        #UFOの耐久力設定
        self.ufo_life = 20
        #ボスの登場条件を設定（UFOを破壊すればTrueになり,ボス登場）
        self.ufo_death = False

    #移動範囲用のメソッド(ランダムであちこちに現れる）
    def move_action(self):
        self.rect.x += random.randint(-350,350)
        self.rect.y += random.randint(-350,350)
        if self.rect.x >= WIDTH or self.rect.x < 100:
            self.rect.x = WIDTH -100
        if self.rect.y >= HEIGHT:
            self.rect.y = HEIGHT - 100  
        if self.rect.y <= 0:
            self.rect.y = 100  
    
    #毎フレームの処理用メソッド 
    def update(self):
        if self.ufo_timer >= 150:
            #上のメソッドを呼び出し
            self.move_action()
            #出現条件の管理
            self.ufo_timer = 100
            self.ufo_move = False
        if self.ufo_death:
            self.kill()
            
        #画像インデックス送り
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]          

#ボスキャラクラス
class Boss(pg.sprite.Sprite):
    def __init__(self,x,y):
        pg.sprite.Sprite.__init__(self)

        self.images = []
        #リストに画像を格納
        for i in range(1,9):         
            image = pg.image.load(f"png/boss/frame-{i}.png").convert_alpha()
            image = pg.transform.scale(image,(705, 509))
            image = pg.transform.flip(image,180,0)     
            self.images.append(image)

        #描画する画像を指定するための設定    
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.radius = 230
        self.dx = 2
        self.dy = 5
        self.life = 50

        #死亡時演出用のタイマー設定
        self.boss_timer = 100
        self.death = False
        
    #毎フレームの処理用メソッド
    def update(self):
        self.rect.y -= self.dy
        self.rect.x -= self.dx
        #move範囲
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.dy *= -1    
        if self.rect.x < 200 or self.rect.x > WIDTH:
            self.dx *= -1
        
        #画像インデックス送り
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

#敵キャラなどの爆発演出用クラス  
# 爆発は複数の画像を一瞬で切り替えて、最後に削除し爆発しているように見せている           
class Explosion(pg.sprite.Sprite):
    def __init__(self,x,y):
        pg.sprite.Sprite.__init__(self)
        
        #画像の設定
        self.explo_imgs = []
        data = pg.image.load('png/explosion_scaled_down.png').convert_alpha()
        #リストに格納
        for col in range(4):
            for row in range(4):
                #スプライトシートから位置、サイズを指定してリストに格納
                img = data.subsurface((32 * row, 32 * col, 32, 32))
                img = pg.transform.scale(img,(72, 72))
                self.explo_imgs.append(img) 

        #描画する画像を指定するための設定 
        self.index = 0
        self.image = self.explo_imgs[self.index]
        self.image.set_colorkey(SKYBLUE)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.radius = int(75 / 2)
        #実行処理時の時間を記録
        self.last_update = pg.time.get_ticks()
        self.speed = 25
        
    #毎フレームの処理用メソッド
    def update(self):
        #実行処理時の時間を記録
        now = pg.time.get_ticks()
        if now - self.last_update > self.speed:
            self.last_update = now
            self.index += 1
            if self.index == len(self.explo_imgs):
                self.kill()
            else:
                self.image = self.explo_imgs[self.index]

#ゲームクラス（メイン処理のクラス）
class Game():
    def __init__(self) -> None:
        #pygameの初期化
        pg.init()
        #サウンドミキサーの初期化
        pg.mixer.init() 
        
        #サウンド関連
        self.BGM = pg.mixer.Sound('mp3/BGM.mp3')
        self.BGM.set_volume(0.2)
        self.BGM.play(-1)
        self.shoot_sound = pg.mixer.Sound('mp3/006.wav')
        self.shoot_sound.set_volume(0.5)
        self.collision_sound = pg.mixer.Sound('mp3/dead.mp3')
        self.falling_sound = pg.mixer.Sound('mp3/dead.wav')
        self.falling_sound.set_volume(0.5)
        self.hit_sound = pg.mixer.Sound('mp3/hit.wav')
        self.hit_sound.set_volume(0.5)
        self.explo_sound = pg.mixer.Sound('mp3/explo.wav')
        self.explo_sound.set_volume(0.5)
        
        #クロック/FPS設定
        self.clock = pg.time.Clock()
        self.fps = 30       

        #画面設定
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        pg.display.set_caption('PlaneGame')
        #マウスのポインターを削除
        pg.mouse.set_visible(False)


        #BGインスタンス化
        self.BG = Background()

        #プレイヤーインスタンス化
        self.plane_group = pg.sprite.Group()
        self.plane = Plane(150,HEIGHT / 2)
        self.plane_group.add(self.plane)
        
        #弾丸関連インスタンス化
        self.bullet_group = pg.sprite.Group()        
        self.explo_group = pg.sprite.Group()       
        
        #ボスインスタンス化
        self.boss_group = pg.sprite.Group()
        self.boss = Boss(WIDTH -1, HEIGHT / 4)
        self.boss_group.add(self.boss)

        #minionインスタンス化        
        self.minion_group = pg.sprite.Group()
        for i in range(20):
            self.minion = Minion(WIDTH + 100 +(50 * i), 50 * i)
            self.minion_group.add(self.minion)    

        #モブ１インスタンス化        
        self.mob_group = pg.sprite.Group()
        for i in range(10):
            self.mob = Mob(WIDTH * 2,random.randint(100,800))
            self.mob_group.add(self.mob)    

        #モブ2インスタンス化  
        self.mob2_group = pg.sprite.Group()
        self.init_Y_position = [-2000,-3000,-4000,-5000,-6000]
        for i in range(15):          
            self.mob2 = Mob2(random.randint(0,WIDTH - 100), random.choice(self.init_Y_position))
            self.mob2_group.add(self.mob2)

        #UFOインスタンス化  
        self.ufo_group = pg.sprite.Group()
        self.ufo = UFO(WIDTH - 100,random.randint(100,HEIGHT - 100))
        self.ufo_group.add(self.ufo)
           
        #スコア
        self.score = 0
        self.hiscore = 0

        #フラグ
        self.BOSS_appear = False
        self.game_over = False
        self.game_clear = False
        self.game_start = True

    #スタート画面の描画用メソッド
    def game_start_screen(self):
        draw_text(self.screen,"Press ENTER KEY TO START", 70, WIDTH / 2, HEIGHT - 500, BLACK)
        draw_text(self.screen,"Press ESCAPE KEY TO EXIT", 50, WIDTH / 2, HEIGHT - 400, BLACK)
        draw_text(self.screen,"BULLET: mouse left click", 50, WIDTH / 2, HEIGHT - 300, BLACK)
        draw_text(self.screen,"MOVE: WASD key", 50, WIDTH / 2, HEIGHT - 200, BLACK)


    #GAMEOVER画面の描画用メソッド
    def game_over_screen(self):
        draw_text(self.screen,"Game Over", 100, WIDTH / 2, HEIGHT / 2, RED)
        draw_text(self.screen,"Press SPACE KEY TO RESTART", 36, WIDTH / 2, HEIGHT - 200, BLACK)
    
    #GAMECLEAR画面の描画用メソッド
    def game_clear_screen(self):
        draw_text(self.screen,"Congratulations!", 100, WIDTH / 2, HEIGHT / 4, YELLOW)
        if self.hiscore < self.score:
            self.hiscore = self.score
        draw_text(self.screen,f"SCORE : {self.score}", 40, WIDTH / 2, int(HEIGHT * 0.4), BLACK)
        draw_text(self.screen,f"HISCORE : {self.hiscore}", 36, WIDTH / 2, int(HEIGHT * 0.5), BLACK)
        draw_text(self.screen,"Press ENTER KEY TO RESTART", 36, WIDTH / 2, int(HEIGHT * 0.8), BLACK)
        draw_text(self.screen,"Press ESCAPE KEY TO EXIT", 36, WIDTH / 2, int(HEIGHT * 0.85), BLACK)
    

    #メインループ
    def main(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                #キー入力の受付
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                    if self.game_start:
                        if event.key == K_RETURN:
                            self.game_start = False

                    #リスタート処理  gameover時　色々初期値に戻す
                    if event.key == pg.K_SPACE:
                        if self.plane.lives == 0:
                            #emptyでグループを空にする
                            self.mob_group.empty()
                            self.boss_group.empty()
                            self.BOSS_appear = False
                            self.game_over = False
                            self.plane.IMMORTAL = False
                            self.plane.lives = 3
                            self.score = 0
                            #プレイヤーのインスタンス化
                            self.plane = Plane(150,HEIGHT / 2)
                            self.plane_group.add(self.plane)
                            self.BGM.play(-1)

                            #ボスのインスタンス化
                            self.boss = Boss(WIDTH - 1, HEIGHT / 4)
                            self.boss_group.add(self.boss)
                            
                            #モブどものインスタンス化
                            for i in range(10):
                                self.mob = Mob(WIDTH,random.randint(100,800))
                                self.mob_group.add(self.mob)
                            
                            for i in range(20):          
                                self.mob2 = Mob2(random.randint(0,WIDTH - 100),random.choice(self.init_Y_position))
                                self.mob2_group.add(self.mob2)

                            for i in range(10):
                                self.minion = Minion(WIDTH + 100 +(50 * i), 50 * -i)
                                self.minion_group.add(self.minion)    
                            
                            #Ufoのインスタンス化
                            self.ufo = UFO(WIDTH - 100,random.randint(100,HEIGHT - 100))
                            self.ufo_group.add(self.ufo)
                            self.ufo.ufo_timer = 0
                            self.ufo.ufo_appear = False
                            self.ufo.ufo_life = 10

                    #リスタート処理　gameClear時
                    if event.key == K_RETURN:
                        if self.game_clear:
                            self.game_clear = False
                            self.plane_group.empty()
                            self.boss_group.empty()
                            self.BOSS_appear = False
                            
                            self.plane.lives = 3
                            self.score = 0

                            #登場キャラクターのインスタンス化
                            self.plane = Plane(150,HEIGHT / 2)
                            self.plane_group.add(self.plane)
                                                        
                            self.boss = Boss(WIDTH - 1, HEIGHT / 4)
                            self.boss_group.add(self.boss)
                            
                            for i in range(10):
                                self.mob = Mob(WIDTH,random.randint(150,int(HEIGHT - 150) ))
                                self.mob_group.add(self.mob)
                            
                            for i in range(20):          
                                self.mob2 = Mob2(random.randint(0,WIDTH - 100),random.choice(self.init_Y_position))
                                self.mob2_group.add(self.mob2)

                            for i in range(10):
                                self.minion = Minion(WIDTH + 100 +(50 * i), 50 * -i)
                                self.minion_group.add(self.minion) 

                            self.ufo = UFO(WIDTH - 100,random.randint(100,HEIGHT - 100))
                            self.ufo_group.add(self.ufo)
                            self.ufo.ufo_timer = 0
                            self.ufo.ufo_appear = False
                            self.ufo.ufo_life = 10
                    
                #弾丸発射キー操作
                if self.game_clear == False and self.game_start == False:
                    if event.type == MOUSEBUTTONDOWN:
                        if self.plane.DEAD == False:
                            self.plane.SHOT,self.plane.IDLE  = True,False
                            self.bullet_group.add(self.plane.create_bullet())
                            self.shoot_sound.play()
                    
                    #マウスボタンを放した時の処理  
                    if event.type == MOUSEBUTTONUP:
                        if self.plane.DEAD == False:             
                            self.plane.IDLE,self.plane.SHOT = True,False
                            self.bullet_READY = True
                            self.shoot_sound.stop()
                    
                   
            #バックグラウンド表示
            self.BG.draw_BG(self.screen)
            if self.game_start:
                self.game_start_screen()
            #残機表示
            if self.game_start == False:
                self.plane.draw_lives(self.screen,20,30)
                
                #ボス出現条件
                if self.ufo.ufo_death:
                    self.BOSS_appear = True
                if self.BOSS_appear:
                    self.boss_group.draw(self.screen)
                    self.boss_group.update()
                    #minion表示
                    self.minion_group.draw(self.screen)
                    self.minion_group.update()
            
                #モブキャラ表示
                self.mob_group.draw(self.screen)
                #爆破描画 
                self.explo_group.draw(self.screen)
                #UFO表示
                self.ufo.ufo_timer += 1
                if self.ufo.ufo_timer > 200:
                    self.ufo.ufo_appear = True
                
                if self.ufo.ufo_appear:
                    self.ufo_group.draw(self.screen)
                    self.ufo_group.update() 

                #モブキャラ2表示
                self.mob2_group.draw(self.screen)
                #プレイヤー、弾丸表示
                self.plane_group.draw(self.screen)
                self.bullet_group.draw(self.screen)

                #各クラスアップデートメソッド実行
                self.plane_group.update()
                self.bullet_group.update()            
                self.mob_group.update()          
                self.mob2_group.update()          
                self.explo_group.update()            
                                                
                #プレイヤーとモブの接触時処理
                if self.plane.DEAD == False and self.plane.IMMORTAL == False:
                    mob1_collision =  pg.sprite.groupcollide(self.plane_group,self.mob_group,False,True)
                    for collision in mob1_collision:                
                        self.plane.DEAD = True
                        self.plane.IDLE, self.plane.SHOT, self.bullet_READY = False, False, False
                        self.BGM.stop()
                        self.collision_sound.play()
                        self.falling_sound.play()
                        self.explo = Explosion(collision.rect.x,collision.rect.y)
                        self.explo_group.add(self.explo)
                        self.plane.lives -= 1
                    
                    mob2_collision =  pg.sprite.groupcollide(self.plane_group,self.mob2_group,False,True)
                    for collision in mob2_collision:                
                        self.plane.DEAD = True
                        self.plane.IDLE,self.plane.SHOT,self.bullet_READY = False, False, False
                        self.BGM.stop()
                        self.collision_sound.play()
                        self.falling_sound.play()
                        self.explo = Explosion(collision.rect.x,collision.rect.y)
                        self.explo_group.add(self.explo)
                        self.plane.lives -= 1 

                    minion_collision =  pg.sprite.groupcollide(self.plane_group,self.minion_group,False,True)
                    for collision in minion_collision:                
                        self.plane.DEAD = True
                        self.plane.IDLE,self.plane.SHOT,self.bullet_READY = False, False, False
                        self.BGM.stop()
                        self.collision_sound.play()
                        self.falling_sound.play()
                        self.explo = Explosion(collision.rect.x,collision.rect.y)
                        self.explo_group.add(self.explo)
                        self.plane.lives -= 1 

                    #ufoと接触時処理               
                    if pg.sprite.collide_circle(self.plane,self.ufo):
                        self.plane.DEAD = True
                        self.plane.IDLE,self.plane.SHOT,self.bullet_READY = False, False, False
                        self.BGM.stop()
                        self.collision_sound.play()
                        self.falling_sound.play()
                        self.plane.lives -= 1 

                    #プレイヤーとボスキャラと接触時処理
                    if pg.sprite.collide_circle(self.plane,self.boss):
                        self.plane.DEAD = True
                        self.plane.IDLE,self.plane.SHOT,self.bullet_READY = False, False, False
                        self.BGM.stop()
                        self.collision_sound.play()
                        self.falling_sound.play()
                        self.plane.lives -= 1

                #プレイヤー死亡時処理
                if self.plane.DEAD == True:
                    if self.plane.rect.top >= HEIGHT:
                        if self.plane.lives == 0:
                            self.plane.kill()
                            self.game_over = True     
                        else:
                            self.plane.IDLE = True
                            self.plane.DEAD = False
                            self.plane.rect.x = 100
                            self.plane.rect.y = HEIGHT / 2
                            self.BGM.play(-1)
                            self.plane.IMMORTAL = True
                
                #モブキャラと弾丸のヒット時の処理
                mob1hits = pg.sprite.groupcollide(self.mob_group,self.bullet_group,True,True)
                if mob1hits:
                    self.score += 100
                    self.hit_sound.play()

                mob2hits = pg.sprite.groupcollide(self.mob2_group,self.bullet_group,True,True)
                if mob2hits:
                    self.score += 200
                    self.hit_sound.play()
                
                minionhits = pg.sprite.groupcollide(self.minion_group,self.bullet_group,True,True)
                if minionhits:
                    self.score += 200
                    self.hit_sound.play()

                #モブ弾丸/ヒット時の処理
                for hit in mob1hits:
                    if self.score <= 5000:               
                        self.mob = Mob(WIDTH,random.randint(100,800))
                        self.mob_group.add(self.mob)
                        self.explo = Explosion(hit.rect.x,hit.rect.y)
                        self.explo_group.add(self.explo)
                    else:
                        self.explo = Explosion(hit.rect.x,hit.rect.y)
                        self.explo_group.add(self.explo)

                for hit in mob2hits:
                    self.explo = Explosion(hit.rect.x,hit.rect.y)
                    self.explo_group.add(self.explo)

                for hit in minionhits:
                    self.explo = Explosion(hit.rect.x,hit.rect.y)
                    self.explo_group.add(self.explo)

                #UFO/弾丸ヒット時
                if self.ufo.ufo_appear:
                    ufohits = pg.sprite.groupcollide(self.bullet_group,self.ufo_group,True,False,pg.sprite.collide_circle)               

                    for hit in ufohits:
                        self.ufo.ufo_life -= 1
                        self.hit_sound.play()
                        self.explo = Explosion(hit.rect.x,hit.rect.y)
                        self.explo_group.add(self.explo)
                        if self.ufo.ufo_life <= 0:
                            self.ufo.ufo_death = True    
                            self.score += 3000
                            self.explo = Explosion(hit.rect.x,hit.rect.y)
                            self.explo_group.add(self.explo)
                            self.explo_sound.play()                

                #ボスキャラ/弾丸ヒット時
                if self.BOSS_appear:
                    bosshits = pg.sprite.groupcollide(self.bullet_group,self.boss_group,True,False,pg.sprite.collide_circle)
                    if bosshits:
                        self.boss.life -= 1
                        if self.boss.life <= 0:
                            self.boss.death = True           

                    for hit in bosshits:
                        self.explo = Explosion(hit.rect.x,hit.rect.y)
                        self.explo_group.add(self.explo)

                #ボス/死亡時        
                if self.boss.death:
                    self.boss.boss_timer -= 1
                    self.explo = Explosion(random.randint(self.boss.rect.x,self.boss.rect.x + 700),random.randint(self.boss.rect.y,self.boss.rect.y + 400))
                    self.explo_group.add(self.explo)
                    if self.boss.boss_timer%5 == 0:
                        self.explo_sound.play()
                    
                    if self.boss.boss_timer < 0:
                        self.boss.kill()
                        self.ufo.kill()
                        self.minion_group.empty()
                        self.score += 10000
                        self.game_clear = True
                        self.plane.IMMORTAL = True   
                        self.boss.death = False


                #スコア表示              
                draw_text(self.screen, f'SCORE: {str(self.score)}', 50, WIDTH / 2, 10, BLACK)
                draw_text(self.screen, f'HISCORE: {str(self.hiscore)}', 50, WIDTH - 140, 10, BLACK)
                
                #GAMEOVER　
                if self.game_over:
                    self.game_over_screen()
                
                #GAME CLEAR
                if self.game_clear:
                    self.mob_group.empty()  
                    self.mob2_group.empty()               
                    self.plane.IMMORTAL =True
                    self.game_clear_screen()
                
                #無敵時間カウンター   
                if self.game_clear == False:
                    if self.plane.IMMORTAL:
                        self.plane.immortal_timer -= 1
                    if self.plane.immortal_timer <= 0:
                        self.plane.IMMORTAL = False
                        self.plane.immortal_timer = 60

            #FPS設定
            self.clock.tick(self.fps)
                
            pg.display.update()
        pg.quit()

game = Game()

game.main()