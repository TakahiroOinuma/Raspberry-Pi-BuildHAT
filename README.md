# Raspberry-Pi-BuildHAT
Raspberry Piを用いてBuildHATを動作させるのに用いたプログラム置き場  

各ファイルの説明  
Raspberry Pi に搭載して動作させるプログラムが以下の三つ  
①　edsigucsv.py　シグモイド関数型のバリア関数を搭載したもの  
②　ednobariacsv.py　バリア関数非搭載のもの  
③　edlinearcsv.py　一次関数型のバリア関数を搭載したもの  

MATLABにて値を定数値で置いて動作させたプログラムが以下  
①allbaria.m  

Raspberry Piを動作させてCSVファイルに記録　そのファイルをMATLABで読み込むために使用した  
CSVファイルおよびMATLABプログラムが以下の４つ  
MATLABファイル  
①CSVyomikomi.m  
CSVファイル  
①　logsigumo.csv　シグモイド関数型の結果  
②　lognobarria.csv　非搭載型の結果  
③　loglinear.csv　一次関数型の結果  
