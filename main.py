import cmd
import shutil
import utils
import json
import os


class TrainData:
    project_name: str
    project_path: str

    image_data_path: str
    images_path: str
    images_output_path: str

    label_data_path: str
    labels_path: str

    final_output_path: str

    def __init__(self, name: str, path: str) -> None:
        self.project_name = name
        self.project_path = path
        utils.make_dir(path)

        self.image_data_path = os.path.join(path, "image_data/")
        utils.make_dir(self.image_data_path)

        self.images_path = os.path.join(path, "images/")
        utils.make_dir(self.images_path)

        self.images_output_path = os.path.join(path, "images_output/")
        utils.make_dir(self.images_output_path)

        self.label_data_path = os.path.join(path, "label_data/")
        utils.make_dir(self.label_data_path)

        self.labels_path = os.path.join(path, "labels/")
        utils.make_dir(self.labels_path)

        self.final_output_path = os.path.join(path, "final_output/")
        utils.make_dir(self.final_output_path)

    def save_project(self) -> dict:
        data = {"name": self.project_name, "path": self.project_path}
        return data

    def unzip_and_rename(self):
        utils.clear_dir(self.images_path)
        files = os.listdir(self.image_data_path)

        for file in files:
            file_path = os.path.join(self.image_data_path, file)
            file_name, file_extension = os.path.splitext(file)
            if file_extension in [".zip"]:
                print("解压: {}".format(file_path))
                unzip_path = os.path.join(self.image_data_path, file_name + "/")
                utils.make_dir(unzip_path)
                # 解压
                shutil.unpack_archive(file_path, unzip_path)
                # 重命名
                utils.rename_dir(unzip_path, file_name)
                # 移动
                utils.move_files(unzip_path, self.images_path)

    def split_image(self, n: int) -> list[str]:
        utils.clear_dir(self.images_output_path)
        utils.train_split_n(self.images_path, self.images_output_path, n)

        dir_files = os.listdir(self.images_output_path)
        result: list[str] = []
        print("开始压缩")
        for dir in dir_files:
            dir_path = os.path.join(self.images_output_path, dir)
            if os.path.isdir(dir_path):
                dir_output_path = os.path.join(self.images_output_path, dir + ".zip")
                # shutil.make_archive(dir_output_path, "zip", dir_path)
                # Only support Linux
                os.system("cd {} && zip -q -r {} {}".format(self.images_output_path, dir_output_path, dir))
                result.append(dir_output_path)

        print("压缩完成")
        return result

    def handle_labels(self):
        # 解压
        files = os.listdir(self.label_data_path)

        for file in files:
            file_path = os.path.join(self.label_data_path, file)
            file_name, file_extension = os.path.splitext(file)
            if file_extension in [".zip"]:
                print("解压: {}".format(file_path))
                unzip_path = os.path.join(self.label_data_path, file_name + "/")
                utils.make_dir(unzip_path)
                # 解压
                shutil.unpack_archive(file_path, unzip_path)

        # 移动标签
        utils.move_files(self.label_data_path, self.labels_path, [".txt"])

    def verify_label(self):
        utils.verify_data(self.images_path, self.labels_path)

    def generate_train_data(self):
        datas = utils.load_data_il(self.images_path, self.labels_path)
        utils.handle_data(datas, self.final_output_path)
        os.system("cd {} && zip -q -r {}.zip final_output".format(self.project_path, self.project_name))


class Main(cmd.Cmd):
    default_project: str = os.path.expanduser("~/labelProject/")
    default_db: str = os.path.join(default_project, "projects.json")
    train_projects: list[TrainData]

    def __init__(self):
        super(Main, self).__init__()
        utils.make_dir(self.default_project)
        self.train_projects = []
        self.load_projects()

    def search_project(self, name: str) -> TrainData | None:
        for project in self.train_projects:
            if project.project_name == name:
                return project
        return None

    def load_projects(self):
        if not os.path.exists(self.default_db):
            with open(self.default_db, "w") as f:
                json.dump({"projects": []}, f)
        with open(self.default_db, "r") as f:
            projects = json.load(f)["projects"]
        for project in projects:
            if os.path.exists(project["path"]):
                train_data = TrainData(project["name"], project["path"])
                self.train_projects.append(train_data)

    def save_projects(self):
        db_data = {"projects": []}
        for project in self.train_projects:
            db_data["projects"].append(project.save_project())

        with open(self.default_db, "w") as f:
            json.dump(db_data, f)

    def do_listproject(self, line: str):
        if len(self.train_projects) == 0:
            print("没有项目")
            return False
        for i, project in enumerate(self.train_projects, 1):
            print("{}: {} | {}".format(i, project.project_name, project.project_path))

    def help_bar(self, line: str):
        print("首先create 创建项目, 移动图片数据到images_data, 运行unzipmove 然后运行 splitimage 就可以完成图片的处理")
        print("handelLabel 处理标签, verifyLabel验证图片和标签的匹配性")
        print("运行generateTrainData 生成最终数据")


    def do_create(self, line: str):
        args = line.split()
        if len(args) != 1:
            print("Need project name")
            return False
        project_path = os.path.join(self.default_project, args[0] + "/")
        self.train_projects.append(TrainData(args[0], project_path))
        self.save_projects()
        print(project_path)

    def do_unzipmove(self, line: str):
        args = line.split()
        if len(args) != 1:
            print("Need project name")
            return False
        project = self.search_project(args[0])
        if project is None:
            print("没找到这个项目")
            return False
        else:
            print("开始解压")
            project.unzip_and_rename()
            print("解压完成")

    def do_splitimage(self, line: str):
        args = line.split()
        if len(args) != 2:
            print("Need project name and split n")
            return False
        project = self.search_project(args[0])
        if project is None:
            print("没找到这个项目")
            return False
        else:
            try:
                n = int(args[1])
            except ValueError:
                print("n 必须是数字")
                return False
            if n <= 0:
                print("n 必须大于0")
                return False
            result = project.split_image(n)
            print("生成好的压缩文件:")
            for zipfile in result:
                print(zipfile)

    def do_handelLabel(self, line: str):
        args = line.split()
        if len(args) != 1:
            print("Need project name and split n")
            return False
        project = self.search_project(args[0])
        if project is None:
            print("没找到这个项目")
            return False
        else:
            project.handle_labels()


    def do_verifyLabel(self, line: str):
        args = line.split()
        if len(args) != 1:
            print("Need project name and split n")
            return False
        project = self.search_project(args[0])
        if project is None:
            print("没找到这个项目")
            return False
        else:
            project.verify_label()

    def do_generateTrainData(self, line: str):
        args = line.split()
        if len(args) != 1:
            print("Need project name and split n")
            return False
        project = self.search_project(args[0])
        if project is None:
            print("没找到这个项目")
            return False
        else:
            project.generate_train_data()

    def do_grent(self, line: str):
        print("Hello")

    def do_EOF(self, line: str):
        return True

    def do_quit(self, line: str):
        return True

if __name__ == "__main__":
    main = Main()
    main.cmdloop()
