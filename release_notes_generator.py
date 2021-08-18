import os
import sys
import asana
from dotenv import load_dotenv
from mdutils.mdutils import MdUtils


class ReleaseNotesGenerator(object):

    def __init__(self, arg1=None):
        self.arg1 = arg1

    load_dotenv()
    project_id = os.getenv('PROJECT_ID')
    section_id = os.getenv('SECTION_ID')
    tag_id = os.getenv('TAG_ID')

    if 'ASANA_TOKEN' in os.environ:
        client = asana.Client.access_token(os.environ['ASANA_TOKEN'])

        try:
            client.users.me()
            print('authorized')
        except:
            print('could not authorize. please get or update ASANA_TOKEN')
            sys.exit(1)

    def initialize_release_notes(self):
        """Sets filename and header

        Returns:
            mdutils: Markdown file to hold list of completed tasks
        """

        release_notes = MdUtils(file_name='release-notes')
        release_notes.new_header(level=1, title='Release notes draft')
        release_notes.title = release_notes.title.replace('\n', '')

        return release_notes

    def get_tasks_with_tag(self):
        """Gets all tasks in the Done section with a particular tag

        Returns:
            list: A list of all tasks, incomplete or complete, with a matching tag_id
        """
        tasks = self.client.tasks.get_tasks_for_section(self.section_id,
                                                        {'opt_fields': ['name', 'custom_fields', 'completed', 'tags']})
        tasks_with_tag = []

        for task in tasks:
            tag_index = 0
            for tag in task['tags']:
                if tag['gid'] != self.tag_id:
                    while tag_index <= len(task['tags']):
                        tag_index += 1
                        continue
                else:
                    tasks_with_tag.append(task)

        if tasks_with_tag:
            return tasks_with_tag
        else:
            print('No tasks were completed for v1.0.0')
            sys.exit()

    def write_tasks(self, task_type, tasks, release_notes):
        """Writes tasks with a matching task type to a Markdown file

        Args:
            task_type (string): The task type to search for
            tasks (list): List of tasks to search through
            release_notes (mdutils): Markdown file to write tasks to

        Returns:
            [mdutils]: Markdown file with task type headings and tasks
        """
        heading_exists = False

        for task in tasks:
            if not task['completed']:
                if task['custom_fields'][2]['display_value'] == task_type:
                    items = [
                        task['name'] + ' ' + '[[View ticket]]' + '(https://app.asana.com/0/' + self.project_id + '/' +
                        task['gid'] + ')']
                    if items is None:
                        print(' ')
                    elif items and (not heading_exists):
                        release_notes.new_header(level=2, title=task_type)
                        release_notes.new_list(items)
                        heading_exists = True
                        continue
                    elif items and heading_exists:
                        release_notes.new_list(items)

        return release_notes

    @staticmethod
    def main():
        """Initializes, writes, and creates a Markdown file that contains a list of tasks with a 2.4 tag and task type
        of New Content, Major Enhancement, Minor Enhancement, or Bug Fix
        """
        release_notes_generator = ReleaseNotesGenerator()
        release_notes = release_notes_generator.initialize_release_notes()
        tasks = release_notes_generator.get_tasks_with_tag()
        release_notes = release_notes_generator.write_tasks('Feature', tasks, release_notes)
        release_notes = release_notes_generator.write_tasks('Bugfix', tasks, release_notes)
        release_notes = release_notes_generator.write_tasks('Hotfix', tasks, release_notes)
        release_notes = release_notes_generator.write_tasks('Testing', tasks, release_notes)

        release_notes.create_md_file()

        print('=====')
        print('complete')
        print('=====')

    if __name__ == '__main__':
        main()
