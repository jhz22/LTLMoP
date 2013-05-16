"""
Extracts Sensor, Actuator, Custom and Region info from spec files
then converts the spec into a language framework
"""

import unittest
import glob
import sys, os
import re
sys.path.append(os.path.join("..","src","lib"))
import specCompiler


class TestExample(unittest.TestCase):
    def __init__(self, spec_filename):
        super(TestExample, self).__init__()
        self.spec_filename = spec_filename

    def runTest(self):
        title_str = "#### Testing project '{0}' ####".format(self.spec_filename)
        fnames = self.spec_filename.rpartition('/') #get the file name without the pwd path as element 2
        print
        print "#"*len(title_str)
        print title_str
        print "#"*len(title_str)

        c = specCompiler.SpecCompiler(self.spec_filename)
        #c_out = c.compile()
        print c.proj.enabled_sensors
        print c.proj.enabled_actuators
        print c.proj.all_customs
        region_names =  [r.name for r in c.proj.rfi.regions]
        print region_names
        fname = fnames[2].replace(".spec",".txt")
	os.system("mkdir pocket_txt")
        s = open("pocket_txt/" + fname,'w')
        
        s.writelines("SENSORS\n")
        for sensor in c.proj.enabled_sensors:
        	s.writelines(sensor)
        	s.writelines("\n")
        s.writelines("ACTUATORS\n")
        for act in c.proj.enabled_actuators:
        	s.writelines(act)
        	s.writelines("\n")
        s.writelines("CUSTOMS\n")
        for cust in c.proj.all_customs:
        	s.writelines(cust)
        	s.writelines("\n")
        s.writelines("REGIONS\n")
        for nm in region_names:
        	s.writelines(nm)
        	s.writelines("\n")
        	
        for rname in region_names:
        	c.specText = re.sub("\\b"+rname+"\\b", "REGION", c.specText)
        for sensor in c.proj.enabled_sensors:
        	c.specText = re.sub("\\b"+sensor+"\\b","SENSOR",c.specText)
        for act in c.proj.enabled_actuators:
        	c.specText = re.sub("\\b"+act+"\\b","ACTUATOR",c.specText)
        for cust in c.proj.all_customs:
        	c.specText = re.sub("\\b"+cust+"\\b","CUSTOM",c.specText)
        
        #print "\n".join(map(lambda s: ">"+s, c.specText.split("\n")))
        s.writelines("FRAMEWORK\n")
        s.writelines(c.specText.replace("\n\n","\n"))


def getTester(spec_filename):
    class NewTester(TestExample): pass
    NewTester.__name__ = "TestExample_" + spec_filename.replace(".","_").replace("\\","_").replace("/","_")
    return NewTester(spec_filename)
    
def suite():
    suite = unittest.TestSuite()
    suite.addTests(getTester(fname) for fname in glob.iglob(os.path.join("..","src","examples","*","*.spec")))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
