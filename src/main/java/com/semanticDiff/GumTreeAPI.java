package com.semanticDiff;

import java.io.IOException;

import com.github.gumtreediff.gen.*;

public class GumTreeAPI {

    private static String getFileExtension(String filePath) {
        return filePath.split("\\.", 0)[1];        
    }
    public static void main(String[] args) throws IOException {
        if(args.length < 2) {
            System.err.println("Insufficient arguments provided.\n" +
            "The task to be performed must be specified first. Either of the following tasks are valid: editscript, jsontree.\n"+
            "In addition the file path to the file(s) to operate on must be supplied.\n" + 
            "editscript Example: java -jar target/semanticDiff-1-jar-with-dependencies.jar editscript version1.py version2.py\n" +
            "jsontree Example: java -jar target/semanticDiff-1-jar-with-dependencies.jar jsontree file.py\n");
            System.exit(1);
        }       

        TreeGenerator treeGenerator = TreeGeneratorFactory.treeGenerator(getFileExtension(args[args.length - 1]));

        if(treeGenerator == null) {
            System.err.println("Unable to find a suitable parser. The programming language specified is currently unsupported.");
            System.exit(1);
        }

        GumTreeTask gumTreeTask = new GumTreeTask(treeGenerator);

        String task = args[0];        
        if(task.equalsIgnoreCase("editscript")) {
            if(args.length != 3) {
                System.err.println("Two files must be provided to create an edit script.");
                System.exit(1);
            }
            else if(!getFileExtension(args[1]).equals(getFileExtension( args[2]))) {
                System.err.println("Both files must be written in the same programming language.");
                System.exit(1);
            }
            gumTreeTask.generateEditScript(args[1], args[2]);
        } 
        else if(task.equalsIgnoreCase("jsontree")) {
            gumTreeTask.printJSONTree(args[1]);
        }
        else {
            System.err.println("Unable to perform the task specified. Either of the following tasks are valid: editscript, jsontree.\n");
            System.exit(1);
        }   
       
    }
}