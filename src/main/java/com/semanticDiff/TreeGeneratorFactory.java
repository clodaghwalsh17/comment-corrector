package com.semanticDiff;

import com.github.gumtreediff.gen.TreeGenerator;
import com.github.gumtreediff.gen.jdt.*;
import com.github.gumtreediff.gen.python.*;
import com.github.gumtreediff.gen.c.*;

public class TreeGeneratorFactory {
    private TreeGeneratorFactory() {      
    }

    public static TreeGenerator treeGenerator(String fileExtension) {
        TreeGenerator gen = null;

        if(fileExtension.isEmpty()) {
            return gen;
        }

        switch(fileExtension) {
            case "java":
                gen = new JdtTreeGenerator();
                break;
            case "py":
                gen = new PythonTreeGenerator();
                break;
            case "c":
            case "h":
                gen = new CTreeGenerator();
                break;
            default:
                return gen;
        }

        return gen;        
    }
   
}
