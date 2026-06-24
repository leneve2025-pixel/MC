# MC
MC的回忆，没啥用
打包命令
pip install pygame pystray pillow natsort
pyinstaller -F -w ^     //打包命令
 --name MC_Jukebox ^   //这里是打包后的名字
 --icon icon.ico ^    //这里是打包后exe的图标
 --add-data "changpian;changpian" ^  //这是音乐文件夹
 --add-data "icon.ico;." ^ //这是添加图标
 MC.py  //这是py文件的名字
