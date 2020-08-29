import os
import unittest

import MaterialX as mx
from MaterialX.PyMaterialXGenShader import *
from MaterialX.PyMaterialXGenOsl import OslShaderGenerator, OSL_UNIFORMS, OSL_OUTPUTS

# Unit tests for GenShader (Python).
class TestGenShader(unittest.TestCase):

    def test_ShaderInterface(self):
        doc = mx.createDocument()

        libraryFolders = ["stdlib"]
        filePath = os.path.dirname(os.path.abspath(__file__))
        searchPath = os.path.join(filePath, "../../libraries")
        mx.loadLibraries(libraryFolders, searchPath, doc)

        exampleName = u"shader_interface"

        # Create a nodedef taking three color3 and producing another color3
        nodeDef = doc.addNodeDef("ND_foo", "color3", "foo")
        fooInputA = nodeDef.addInput("a", "color3")
        fooInputB = nodeDef.addInput("b", "color3")
        fooOutput = nodeDef.getOutput("out")
        fooInputA.setValue(mx.Color3(1.0, 1.0, 0.0))
        fooInputB.setValue(mx.Color3(0.8, 0.1, 0.1))

        # Create an implementation graph for the nodedef performing
        # a multiplication of the three colors.
        nodeGraph = doc.addNodeGraph("IMP_foo")
        nodeGraph.setAttribute("nodedef", nodeDef.getName())

        output = nodeGraph.addOutput(fooOutput.getName(), "color3")
        mult1 = nodeGraph.addNode("multiply", "mult1", "color3")
        in1 = mult1.addInput("in1", "color3")
        in1.setInterfaceName(fooInputA.getName())
        in2 = mult1.addInput("in2", "color3")
        in2.setInterfaceName(fooInputB.getName())
        output.setConnectedNode(mult1)

        doc.addNode("foo", "foo1", "color3")
        output = doc.addOutput("foo_test", "color3");
        output.setNodeName("foo1");
        output.setAttribute("output", "o");

        shadergen = OslShaderGenerator.create()
        context = GenContext(shadergen)
        context.registerSourceCodeSearchPath(searchPath)

        # Test complete mode
        context.getOptions().shaderInterfaceType = int(ShaderInterfaceType.SHADER_INTERFACE_COMPLETE);
        shader = shadergen.generate(exampleName, output, context);
        self.assertTrue(shader)
        self.assertTrue(len(shader.getSourceCode(PIXEL_STAGE)) > 0)

        ps = shader.getStage(PIXEL_STAGE);
        uniforms = ps.getUniformBlock(OSL_UNIFORMS)
        self.assertTrue(uniforms.size() == 2)

        outputs = ps.getOutputBlock(OSL_OUTPUTS)
        self.assertTrue(outputs.size() == 1)
        self.assertTrue(outputs[0].getName() == output.getName())

        file = open(shader.getName() + "_complete.osl", "w+")
        file.write(shader.getSourceCode(PIXEL_STAGE))
        file.close()
        os.remove(shader.getName() + "_complete.osl");

        context.getOptions().shaderInterfaceType = int(ShaderInterfaceType.SHADER_INTERFACE_REDUCED);
        shader = shadergen.generate(exampleName, output, context);
        self.assertTrue(shader)
        self.assertTrue(len(shader.getSourceCode(PIXEL_STAGE)) > 0)

        ps = shader.getStage(PIXEL_STAGE);
        uniforms = ps.getUniformBlock(OSL_UNIFORMS)
        self.assertTrue(uniforms.size() == 0)

        outputs = ps.getOutputBlock(OSL_OUTPUTS)
        self.assertTrue(outputs.size() == 1)
        self.assertTrue(outputs[0].getName() == output.getName())

        file = open(shader.getName() + "_reduced.osl", "w+")
        file.write(shader.getSourceCode(PIXEL_STAGE))
        file.close()
        os.remove(shader.getName() + "_reduced.osl");

if __name__ == '__main__':
    unittest.main()
