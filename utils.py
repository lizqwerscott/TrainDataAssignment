import os
import zipfile
import json
import shutil
import random


def make_dir(path: str):
    if not os.path.exists(path):
        os.mkdir(path)


def list_split(lst: list, n: int):
    n_size = int(len(lst) / n)
    result = []
    for i in range(0, n):
        result.append(lst[i * n_size : n_size + i * n_size])

    result[-1].extend(lst[n * n_size : len(lst)])
    return result

def move_files(path: str, output: str, file_extensions: list[str] = [".jpg"]):
    files: list[str] = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if file_extension in file_extensions:
                file_now_path = os.path.join(root, file)
                file_new_path = os.path.join(output, file)
                shutil.move(file_now_path, file_new_path)

def load_data(path: str) -> list:
    result: list[dict] = []

    for root, dirs, files in os.walk(path):
        for name in files:
            file_name, file_extension = os.path.splitext(name)

            find_p = None
            for item in result:
                if item["name"] == file_name:
                    find_p = item
                    break

            if find_p != None:
                find_p = {}
                if file_extension in [".jpg", ".png"]:
                    find_p["image"] = os.path.join(root, name)
                elif file_extension == ".txt":
                    find_p["label"] = os.path.join(root, name)
                else:
                    print("error: {}".format(os.path.join(root, name)))
            else:
                data = {}
                data["name"] = file_name
                if file_extension in [".jpg", ".png"]:
                    data["image"] = os.path.join(root, name)
                elif file_extension == ".txt":
                    data["label"] = os.path.join(root, name)

                if len(data.keys()) == 2:
                    result.append(data)

    return result


def load_data_il(images_path: str, labels_path: str) -> list:
    result: list[dict] = []

    for image in os.listdir(images_path):
        image_name, _ = os.path.splitext(image)

        data = {}
        data["name"] = image_name
        data["image"] = os.path.join(images_path, image)

        for label in os.listdir(labels_path):
            label_name, _ = os.path.splitext(label)
            if label_name == image_name:
                data["label"] = os.path.join(labels_path, label)
                break
        result.append(data)

    return result


def split_train_var(data: list, scale: list):
    length = len(data)
    val_len = int(length * scale[1] * 0.1)
    test_len = int(length * scale[2] * 0.1)
    if val_len == 0:
        val_len = 1
    if test_len == 0:
        test_len = 1

    if scale[1] == 0:
        val_len = 0

    test_list = data[0:test_len]
    val_list = data[test_len : test_len + val_len]
    train_list = data[test_len + val_len : -1]

    return (train_list, val_list, test_list)


def move_train_data(output_path: str, data: list):
    images_path = "{}{}/".format(output_path, "images")
    labels_path = "{}{}/".format(output_path, "labels")

    make_dir(images_path)
    make_dir(labels_path)

    for file in data:
        picture_name = os.path.basename(file["image"])
        label_name = os.path.basename(file["label"])

        shutil.copy(file["image"], "{}{}".format(images_path, picture_name))
        shutil.copy(file["label"], "{}{}".format(labels_path, label_name))


def handle_data(data: list, result_path: str, split_scale=[7, 1, 2]):

    random.shuffle(data)

    train_list, val_list, test_list = split_train_var(data, split_scale)

    train_path = "{}{}/".format(result_path, "train")
    val_path = "{}{}/".format(result_path, "val")
    test_path = "{}{}/".format(result_path, "test")

    make_dir(train_path)
    make_dir(val_path)
    make_dir(test_path)

    move_train_data(train_path, train_list)
    move_train_data(val_path, val_list)
    move_train_data(test_path, test_list)


def verify_data(image_path: str, label_path: str):
    image_list = os.listdir(image_path)
    label_list = os.listdir(label_path)

    no_images: list[str] = []
    no_labels: list[str] = []

    for image in image_list:
        a = os.path.splitext(image)[0]
        is_have = False

        for label in label_list:
            if label == a + ".txt":
                is_have = True
                break

        if not is_have:
            no_images.append(image)
            print(image)

    for label in label_list:
        a = os.path.splitext(label)[0]
        is_have = False

        for image in image_list:
            if a in image:
                is_have = True
                break

        if not is_have:
            no_labels.append(label)
            print(label)


def rename_dir(dir: str, add_name: str):
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            file_last_name = os.path.join(root, file)
            file_new_name = os.path.join(root, "{}_{}{}".format(file_name, add_name, file_extension))
            os.rename(file_last_name, file_new_name)

def train_split_n(train_path: str, output_path: str, n: int):
    file_lst = os.listdir(train_path)

    print("The all is {}".format(len(file_lst)))

    data = list_split(file_lst, n)

    i = 0
    for files in data:
        print("The {} len is {}".format(i, len(files)))

    i = 0
    for files in data:
        for file_name in files:
            dir_path = output_path + str(i) + "/"
            make_dir(dir_path)
            shutil.copy(train_path + file_name, output_path + str(i) + "/" + file_name)
        i += 1

def clear_dir(dir: str):
    shutil.rmtree(dir)
    make_dir(dir)


if __name__ == "__main__":
    data_path = "./data/"
    result_path = "./output/"

    make_dir(data_path)
    make_dir(result_path)

    datas = load_data(data_path)

    handle_data(datas, result_path)

    # verify_data("./data/images/", "./data/label/")
