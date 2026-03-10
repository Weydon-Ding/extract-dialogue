from argparse import Action, ArgumentParser

from .config import Config, ModelPlatform


class ListPlatformsAction(Action):
    """自定义Action，用于列出支持的平台"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print("=== 支持的模型平台 ===")
        for name, description in ModelPlatform.list_platforms().items():
            print(f"  {name}: {description}")
        print(f"\n当前默认平台: {Config.CURRENT_PLATFORM}")
        parser.exit()


class Argument:
    """命令行参数解析器"""

    def __init__(self):
        parser = ArgumentParser(description='从小说中提取角色对话')
        parser.add_argument('input_file', nargs='?', help='输入文本文件路径')
        parser.add_argument('-o', '--output', help='输出文件路径（可选）')
        parser.add_argument('--stats', action='store_true', default=Config.DEFAULT_SHOW_STATS, help='显示统计信息 (默认: 开启)')
        parser.add_argument('--no-stats', action='store_false', dest='stats', help='不显示统计信息')
        parser.add_argument('-p', '--platform', help='指定使用的平台 (如: deepseek, openai, moonshot等)')
        parser.add_argument('-l', '--list-platforms', action=ListPlatformsAction, help='列出所有支持的平台')
        parser.add_argument('-t', '--threads', type=int, default=Config.MAX_WORKERS, help=f'指定并发线程数 (默认: {Config.MAX_WORKERS})')
        parser.add_argument('--concurrent', action='store_true', default=Config.DEFAULT_CONCURRENT, help='使用多线程并发处理 (默认: 开启)')
        parser.add_argument('--no-concurrent', action='store_false', dest='concurrent', help='使用单线程处理')
        parser.add_argument('--no-chunk-id', action='store_true', help='不在输出中包含chunk-id信息')
        parser.add_argument('--save-chunk-text', action='store_true', default=Config.DEFAULT_SAVE_CHUNK_TEXT, help='保存原始chunk文本 (默认: 开启)')
        parser.add_argument('--no-save-chunk-text', action='store_false', dest='save_chunk_text', help='不保存原始chunk文本')
        parser.add_argument('--sort-output', action='store_true', default=Config.DEFAULT_SORT_OUTPUT, help='完成后按chunk_id排序输出文件 (默认: 开启)')
        parser.add_argument('--no-sort-output', action='store_false', dest='sort_output', help='不排序输出文件')
        parser.add_argument('--legacy-format', action='store_true', help='同时生成旧格式文件（不含chunk_id）')

        self.__args = parser.parse_args()

        # 检查是否提供了输入文件
        if not self.__args.input_file:
            parser.error("请提供输入文件路径")

    @property
    def input_file(self)-> str:
        return self.__args.input_file

    @property
    def output(self) -> str:
        return self.__args.output

    @property
    def stats(self) -> bool:
        return self.__args.stats

    @property
    def platform(self) -> str:
        return self.__args.platform

    @property
    def threads(self) -> int:
        return self.__args.threads

    @property
    def concurrent(self) -> bool:
        return self.__args.concurrent

    @property
    def no_chunk_id(self) -> bool:
        return self.__args.no_chunk_id

    @property
    def save_chunk_text(self) -> bool:
        return self.__args.save_chunk_text

    @property
    def sort_output(self) -> bool:
        return self.__args.sort_output

    @property
    def legacy_format(self) -> bool:
        return self.__args.legacy_format


instance = Argument()

__all__ = ['instance']
