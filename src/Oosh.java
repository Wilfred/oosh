import java.io.Console;

class Oosh {
    public static void main(String[] args) {
	Console console = System.console();
	console.printf("Welcome to oosh\n");

	while(true) {
	    String currentLine = console.readLine("$ ");
	    execute(currentLine);
	}
    }

    private static void execute(String command) {
	//todo: need to register commands properly
	if (command.equals("exit")) {
	    System.exit(0);
	} else {
	    System.out.printf("oosh: command \"%s\"" +
			      " not found\n",command);
	}
    }
}