package com.semanticDiff;

import java.io.IOException;

// import com.github.gumtreediff.client.Run;
// import com.github.gumtreediff.gen.*;
import com.github.gumtreediff.gen.jdt.*;
import com.github.gumtreediff.matchers.*;
import com.github.gumtreediff.actions.*;
import com.github.gumtreediff.actions.model.*;
import com.github.gumtreediff.tree.*;


public class GumTreeAPI {
    // public static void main(String[] args) throws UnsupportedOperationException, IOException {
    //     Run.initGenerators(); // registers the available parsers
    //     String srcFile = "ExampleA.java";
    //     String dstFile = "ExampleB.java";
    //     Tree src = TreeGenerators.getInstance().getTree(srcFile).getRoot(); // retrieves and applies the default parser for the file 
    //     Tree dst = TreeGenerators.getInstance().getTree(dstFile).getRoot(); // retrieves and applies the default parser for the file 
    //     Matcher defaultMatcher = Matchers.getInstance().getMatcher(); // retrieves the default matcher
    //     MappingStore mappings = defaultMatcher.match(src, dst); // computes the mappings between the trees
    //     EditScriptGenerator editScriptGenerator = new SimplifiedChawatheScriptGenerator(); // instantiates the simplified Chawathe script generator
    //     EditScript actions = editScriptGenerator.computeActions(mappings); // computes the edit script
    //     System.out.println(actions);
    // }

    public static void main(String[] args) throws IOException {
        if(args.length != 2) {
            System.err.println("Two files must be provided to perform semantic differencing");
            System.exit(1);
        } 

        String srcFile = args[0];
        String dstFile = args[1];

        Tree src = new JdtTreeGenerator().generateFrom().file(srcFile).getRoot();
        Tree dst = new JdtTreeGenerator().generateFrom().file(dstFile).getRoot();
        Matcher defaultMatcher = Matchers.getInstance().getMatcher(); // retrieves the default matcher
        MappingStore mappings = defaultMatcher.match(src, dst); // computes the mappings between the trees
        EditScriptGenerator editScriptGenerator = new SimplifiedChawatheScriptGenerator(); // instantiates the simplified Chawathe script generator
        EditScript actions = editScriptGenerator.computeActions(mappings);
        
        for(Action a: actions) {
            System.out.println(a);
        }
    }

}