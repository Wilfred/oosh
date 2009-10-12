/*  oosh: an object oriented shell
    Copyright (C) 2009 Wilfred Hughes
 
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
 
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program. If not, see
    <http://www.gnu.org/licenses/>.
*/

import java.io.Console;
import sun.misc.Signal;
import sun.misc.SignalHandler;

class Oosh {
    public static void main(String[] args) {
	Console console = System.console();
	console.printf("Welcome to oosh\n");

	Signal.handle(new Signal("INT"), new SignalHandler() {
		// Signal handler method
		public void handle(Signal signal) {
		    //do nothing, user should use exit
		}
	    });

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