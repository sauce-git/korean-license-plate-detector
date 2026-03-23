import glob
import os
import shutil

# 파일 위치 초기화 및 설정
path = os.path.dirname(os.path.realpath(__file__))
path = path + '\\' + 'original-images' # 분류할 파일이 저장된 폴더를 지정해준다
os.chdir(path) # 현재 위치 지정

extensions = [] # 폴더 내 모든 확장자 목록

read_files = glob.glob("*.*") # file 폴더 내 파일 목록 추출

# 확장자 추출 및 해당 목록에 추가
for file in read_files:
    loc = file.rfind('.')
    extensions.append(file[loc+1:])

extensions = list(dict.fromkeys(extensions)) # 중복 확장자 목록에서 제거

# 각 확장자에 해당하는 폴더 생성
for item in extensions:
    os.mkdir(item)

# 모든 파일의 확장자 확인 후 해당 폴더로 이동
for item in extensions:
    for file in read_files:
        if item in file:
            shutil.move(file, path + '\\' + item + '\\' + file)

# 완료 메세지
print(f"총 {len(read_files)}개의 파일이 분류되었습니다.")