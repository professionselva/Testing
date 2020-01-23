import sys, os
d = os.path.split(os.getcwd())[0]
sys.path.append(d)
from unittest import TestLoader, TestSuite, TestCase
from unittest.loader import _FailedTest
import xmlrunner
from optparse import OptionParser
from srux_automation import srux_path
from srux_automation import config
import json
import HtmlTestRunner


class TestRunner:
    @staticmethod
    def get_names_from_tag(tag, test_folder):
        tag_file = tag + ".json"
        tag_file_path = os.path.join(srux_path, test_folder, "srux_tags", tag_file)
        f = open(tag_file_path)
        content = f.read()
        f.close()
        return json.loads(content)

    @staticmethod
    def get_module_name(sub_test):
        if sub_test.countTestCases() > 0:
            print(str(sub_test))
            if isinstance(sub_test, _FailedTest):
                return sub_test._testMethodName
            elif not isinstance(sub_test, TestSuite):
                return sub_test.__module__
            else:
                for sub in sub_test:
                    if sub.countTestCases() > 0: #Inheritance
                        return TestRunner.get_module_name(sub)

    @staticmethod
    def get_single_test_case(sub_test, single_test):
        if sub_test.countTestCases() > 0:
            for sub in sub_test:
                if sub.countTestCases() > 0:  # Inheritance
                    for test in sub._tests:
                        if isinstance(test, TestCase):
                            if test._testMethodName.startswith(single_test):
                                return test #._testMethodName#id()


    @staticmethod
    def start(test_path, module_test, single_test, tag, xml_report=False, open_browser=False, suffix="Automation_Report"):

        loader = TestLoader()
        all_tests = loader.discover(start_dir=test_path)
        suite = TestSuite()

        if module_test:
            for sub_test in all_tests:
                module_name = TestRunner.get_module_name(sub_test) #refactor, after get_module_name() it is necessary to check for empty lists again
                if module_name and module_name.endswith(module_test):
                    if single_test:
                        single_test_case = TestRunner.get_single_test_case(sub_test, single_test)
                        if single_test_case is not None:
                            single_test_case_suite = TestSuite()
                            single_test_case_suite.addTest(single_test_case)
                            suite.addTest(single_test_case_suite)
                    else:
                        suite.addTest(sub_test)


        elif tag and tag != "regression":
            test_names = TestRunner.get_names_from_tag(tag, test_path)
            for test_name in test_names:
                for sub_test in all_tests:
                    module_name = TestRunner.get_module_name(sub_test)
                    if module_name and module_name.endswith(test_name):
                        suite.addTest(sub_test)
        else:
            suite.addTest(all_tests)

        if xml_report:
            xmlrunner.XMLTestRunner(output='xml-reports', outsuffix=suffix).run(suite)
        else:
            HtmlTestRunner.HTMLTestRunner(combine_reports=True,
                                          report_name="Automation_Report",
                                          add_timestamp=True,
                                          open_in_browser=open_browser,
                                          report_title=tag,
                                          template=report_template_path
                                          ).run(suite)

if __name__ == "__main__":

    parser = OptionParser()

    parser.add_option("-o",
                      "--open-browser",
                      dest="open_browser",
                      action="store_true",
                      default=False,
                      help="Open automatically the browser when a test is run")

    parser.add_option("-f",
                      "--test-folder",
                      dest="test_folder",
                      default="tests",
                      help="Test folder where you have the testcases, by default is tests ")

    parser.add_option("-t",
                      "--tag",
                      dest="tag",
                      default="regression",
                      help="Tag to define which Test Cases are going to be execute. Should be the same as the "
                           "file name of the json to run ")

    parser.add_option("-r",
                      "--report-template-path",
                      dest="report_template_path",
                      help="report template path to use. Default will be on TestUtility/report_teplate.html")

    parser.add_option("-m",
                      "--module-test",
                      dest="module_test",
                      help="name of the test module/suite to run")

    parser.add_option("-s",
                      "--single-test",
                      dest="single_test",
                      help="name of a single test to run")

    parser.add_option("-x",
                      "--xml-report",
                      dest="xml_report",
                      action="store_true",
                      default=False,
                      help="define if the report will be created in xml. ")

    (options, args) = parser.parse_args()

    test_folder = options.test_folder

    report_template_path = os.path.join(srux_path, "utilities", "report_template.html")
    if options.report_template_path:
        report_template_path = options.report_template_path

    test_path = os.path.join(srux_path, test_folder)
    sys.path.append(test_path)
    user_cfg = os.path.join(test_path, "user.cfg")
    if os.path.isfile(user_cfg):
        config.read(user_cfg)

    config.set("PROJECT", "test_path", test_path)

    TestRunner.start(test_path, options.module_test, options.single_test, options.tag, options.xml_report, options.open_browser)



