package com.semanticDiff;

import java.io.IOException;

import com.github.gumtreediff.gen.*;
import com.github.gumtreediff.io.TreeIoUtils;
import com.github.gumtreediff.matchers.*;
import com.github.gumtreediff.actions.*;
import com.github.gumtreediff.actions.model.*;
import com.github.gumtreediff.tree.*;

public class GumTreeTask {
    private TreeGenerator treeGenerator;

    public GumTreeTask(TreeGenerator treeGenerator) {
        this.treeGenerator = treeGenerator;
    }

    public void generateEditScript(String srcFile, String dstFile) throws IOException {
        Tree src = this.treeGenerator.generateFrom().file(srcFile).getRoot();
        Tree dst = this.treeGenerator.generateFrom().file(dstFile).getRoot();
        Matcher defaultMatcher = Matchers.getInstance().getMatcher(); 
        MappingStore mappings = defaultMatcher.match(src, dst); 
        EditScriptGenerator editScriptGenerator = new SimplifiedChawatheScriptGenerator(); 
        EditScript actions = editScriptGenerator.computeActions(mappings);
        
        for(Action a: actions) {
            System.out.println(a);
        }
    }

    public void printJSONTree(String file) throws IOException{
        TreeContext treeContext = this.treeGenerator.generateFrom().file(file);
        System.out.println(TreeIoUtils.toJson(treeContext));
    }
}
