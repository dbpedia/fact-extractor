package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/1/13
 * Time: 1:53 PM
 * To change this template use File | Settings | File Templates.
 */
public class Token {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>Token</code>.
	 */
	static Logger logger = Logger.getLogger(Token.class.getName());

	int num;

	String  form;

	String pos;

	String frame;

	String role;

	boolean target;

	public Token() {
	}

	Token(String[] s) {
		num = new Integer(s[0]);
		form = s[1];
		pos = s[2];
		frame = s[3];
		role = s[4];
		if (s[4].equalsIgnoreCase("target"))
		{
			target = true;
		}
		else
		{
			target = false;
		}
	}

	public void setNum(int num) {
		this.num = num;
	}

	public void setForm(String form) {
		this.form = form;
	}

	public void setPos(String pos) {
		this.pos = pos;
	}

	public void setFrame(String frame) {
		this.frame = frame;
	}

	public void setRole(String role) {
		this.role = role;
	}

	public void setTarget(boolean target) {
		this.target = target;
	}

	public int getNum() {
		return num;
	}

	public String getForm() {
		return form;
	}

	public String getPos() {
		return pos;
	}

	public String getFrame() {
		return frame;
	}

	public String getRole() {
		return role;
	}

	public boolean isTarget() {
		return target;
	}


}
