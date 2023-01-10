package com.semanticDiff;

import java.io.IOException;

import com.github.gumtreediff.gen.*;
import com.github.gumtreediff.io.TreeIoUtils;
import com.github.gumtreediff.matchers.*;
import com.github.gumtreediff.actions.*;
import com.github.gumtreediff.actions.model.*;
import com.github.gumtreediff.tree.*;

public class GumTreeAPI {
    public static void main(String[] args) throws IOException {
        if(args.length != 3) {
            System.err.println("Insufficient arguments provided. \nThe programming language of the source files, as well as the file path to two files must be provided to perform semantic differencing");
            System.exit(1);
        } 

        String programmingLanguage = args[0];
        String srcFile = args[1];
        String dstFile = args[2];

        TreeGenerator treeGenerator = TreeGeneratorFactory.treeGenerator(programmingLanguage);

        if(treeGenerator == null) {
            System.err.println("Unable to find a suitable parser. The programming language specified is currently unsupported.");
            System.exit(1);
        }

        Tree src = treeGenerator.generateFrom().file(srcFile).getRoot();
        Tree dst = treeGenerator.generateFrom().file(dstFile).getRoot();
        Matcher defaultMatcher = Matchers.getInstance().getMatcher(); 
        MappingStore mappings = defaultMatcher.match(src, dst); 
        EditScriptGenerator editScriptGenerator = new SimplifiedChawatheScriptGenerator(); 
        EditScript actions = editScriptGenerator.computeActions(mappings);
        
        for(Action a: actions) {
            System.out.println(a);
        }

        TreeContext treeContext = treeGenerator.generateFrom().file(dstFile);
        System.out.println("\n----------------------- JSON Format of tree -----------------------\n");
        System.out.println(TreeIoUtils.toJson(treeContext));
    }
}