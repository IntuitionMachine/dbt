
from dbt.contracts.graph.unparsed import UnparsedNode
from dbt.node_types import NodeType
from dbt.parser.base import MacrosKnownParser
from dbt.parser.base_sql import BaseSqlParser, SQLParseResult

import dbt.clients.jinja
import dbt.exceptions
import dbt.utils

import jinja2

import os


class ArchiveParser(MacrosKnownParser):
    @classmethod
    def parse_archives_from_project(cls, config):
        archives = []
        archive_configs = config.archive

        for archive_config in archive_configs:
            tables = archive_config.get('tables')

            if tables is None:
                continue

            for table in tables:
                cfg = table.copy()
                cfg['source_database'] = archive_config.get(
                    'source_database',
                    config.credentials.database
                )
                cfg['target_database'] = archive_config.get(
                    'target_database',
                    config.credentials.database
                )

                cfg['source_schema'] = archive_config.get('source_schema')
                cfg['target_schema'] = archive_config.get('target_schema')

                fake_path = [cfg['target_database'], cfg['target_schema'],
                             cfg['target_table']]
                archives.append({
                    'name': table.get('target_table'),
                    'root_path': config.project_root,
                    'resource_type': NodeType.Archive,
                    'path': os.path.join('archive', *fake_path),
                    'original_file_path': 'dbt_project.yml',
                    'package_name': config.project_name,
                    'config': cfg,
                    'raw_sql': '{{config(materialized="archive")}} -- noop'
                })

        return archives

    def load_and_parse(self):
        """Load and parse archives in a list of projects. Returns a dict
           that maps unique ids onto ParsedNodes"""

        archives = []
        to_return = {}

        for name, project in self.all_projects.items():
            archives = archives + self.parse_archives_from_project(project)

        # We're going to have a similar issue with parsed nodes, if we want to
        # make parse_node return those.
        for a in archives:
            # archives have a config, but that would make for an invalid
            # UnparsedNode, so remove it and pass it along to parse_node as an
            # argument.
            archive_config = a.pop('config')
            archive = UnparsedNode(**a)
            node_path = self.get_path(archive.resource_type,
                                      archive.package_name,
                                      archive.name)

            to_return[node_path] = self.parse_node(
                archive,
                node_path,
                self.all_projects.get(archive.package_name),
                archive_config=archive_config)

        return to_return


class ArchiveBlockParser(BaseSqlParser):
    # def parse_archives_from_file(self, file_node, tags=None):
    #     # the file node has a 'raw_sql' field that contains the jinja data with
    #     # (we hope!) `archive` blocks
    #     name_pattern = r'[A-Za-z_][A-Za-z0-9_]*'
    #     block_begin = r'(?:\s*{0}\-|{0})'.format(re.escape('{%'))
    #     block_end = r'(?:\-{0}\s%|{0})'.format(re.escape('%}'))

    #     start_pat = r'(?P<begin>({})\s*archive\s+(?P<name>({}))({}))'.format(
    #             block_begin, name_pattern, block_end
    #     )

    #     end_pat = r'(.*?)({}\s*endarchive\s*{})'.format(block_begin, block_end)
    #     full_pat = '{}(?P<body>(.*)){}'.format(start_pat, end_pat)

    #     blocks = re.findall(full_pat, file_node.raw_sql,
    #                         flags=re.DOTALL|re.MULTILINE)

    #     import ipdb;ipdb.set_trace()
    #     for block in blocks:
    #         groups = block.groupdict()

    #     try:
    #         template = dbt.clients.jinja.get_template(file_node.raw_sql, {})
    #     except dbt.exceptions.CompilationException as e:
    #         if e.node is None:
    #             e.node = file_node
    #         raise

    #     for key, item in template.module.__dict__.items():
    #         if type(item) != jinja2.runtime.Macro:
    #             continue

    #         if not key.startswith(dbt.utils.ARCHIVE_PREFIX):
    #             continue

    #         name = key.replace(dbt.utils.ARCHIVE_PREFIX, '')

    #         unique_id = 'archive.{}.{}'.format(file_node.package_name, name)
    #         fqn = self.get_fqn(file_node.path,
    #                            self.all_projects[file_node.package_name])
    #         raw_sql = item().strip()
    #         yield file_node.incorporate(raw_sql=raw_sql, name=name,
    #                                     unique_id=unique_id, fqn=fqn)

    @classmethod
    def get_compiled_path(cls, name, relative_path):
        return os.path.join('analysis', relative_path)

    def parse_sql_nodes(self, nodes, tags=None):
        if tags is None:
            tags = []
        import ipdb;ipdb.set_trace()
        return super(ArchiveBlockParser, self).parse_sql_nodes(nodes, tags)

        results = SQLParseResult()

        # in archives, we have stuff in blocks.
        for file_node in nodes:
            archive_nodes = list(
                self.parse_archives_from_file(file_node, tags=tags)
            )
            found = super(ArchiveBlockParser, self).parse_sql_nodes(
                nodes=archive_nodes, tags=tags
            )
            results.update(found)
        return results
