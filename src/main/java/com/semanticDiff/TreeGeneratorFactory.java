package com.semanticDiff;

import com.github.gumtreediff.gen.TreeGenerator;
import com.github.gumtreediff.gen.jdt.*;
import com.github.gumtreediff.gen.python.*;
import com.github.gumtreediff.gen.c.*;

public class TreeGeneratorFactory {
    private TreeGeneratorFactory() {      
    }

    public static TreeGenerator treeGenerator(String programmingLanguage) {
        TreeGenerator gen = null;

        if(programmingLanguage.isEmpty()) {
            return gen;
        }

        switch(programmingLanguage) {
            case "Java":
                gen = new JdtTreeGenerator();
                break;
            case "Python":
                gen = new PythonTreeGenerator();
                break;
            case "C":
                gen = new CTreeGenerator();
                break;
            default:
                return gen;
        }

        return gen;        
    }
}
