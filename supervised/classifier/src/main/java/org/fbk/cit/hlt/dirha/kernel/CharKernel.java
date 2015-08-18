package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.util.Arrays;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/4/13
 * Time: 10:08 AM
 * To change this template use File | Settings | File Templates.
 */
public class CharKernel {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>CharKernel</code>.
	 */
	static Logger logger = Logger.getLogger(CharKernel.class.getName());
	//
	private double lambda;

	//
	private int length;

	//
	public CharKernel(double lambda, int length) {
		this.lambda = lambda;
		this.length = length;

		//logger.info("lambda: " + lambda);
		//logger.info("length: " + length);
	} // end constructor

	//
	public double get(String s1, String s2)
	{
		return k(s1.toCharArray(), s2.toCharArray(), length);
	} // end compare

	//
	private double k(char[] s, char[] t, int n)
	{
		//logger.debug(Arrays.toTable(s) + "," + Arrays.toTable(t));
		//logger.debug("k('" + new String(s) + "', '" + new String(t) + "', " + n + ")");
		//logger.debug("k(" + s + ", " + t +")");
		if (Math.min(s.length, t.length) < n)
		{
			//logger.debug("k.return 0");
			return 0;
		}

		char[] p = prefix(s);
		char x = last(s);

		//logger.debug("k.p: " + new String(p));
		//logger.debug("k.x: " + x);

		return k(p, t, n) + sumk(p, t, x, n-1);
	} // end k

	//
	private double sumk(char[] s, char[] t, char x, int n)
	{
		//logger.debug("sumk('" + new String(s) + "', '" + new String(t) + "', '" +  x + "', " + n + ")");

		double sum = 0;

		for (int j=0;j<t.length;j++)
		{
			//logger.debug("sumk.t[" + j + "]='" + t[j] + "' vs. '" + x + "'");

			if (t[j] == x)
			{
				//logger.debug("sumk.t[" + j + "]='" + x + "'");
				sum += kp(s, prefix(t, j), n) * Math.pow(lambda, 2);
				//logger.debug("sumk.sum[1.." + j + "]=" + sum);
			}
		}

		//logger.debug("sumk.sum: " + sum);
		return sum;
	} // end sumk

	//
	private double kp(char[] s, char[] t, int n)
	{
		//logger.debug("kp('" + new String(s) + "', '" + new String(t) + "', " + n + ")");

		if (n == 0)
		{
			//logger.debug("kp.return 1");
			return 1;
		}

		if (Math.min(s.length, t.length) < n)
		{
			//logger.debug("kp.return 0");
			return 0;
		}

		char[] p = prefix(s);
		char x = last(s);

		return (lambda * kp(p, t, n)) + sumkp(p, t, x, n-1);
	} // end kp

	//
	private double sumkp(char[] s, char[] t, char x, int n)
	{
		//logger.debug("sumkp('" + new String(s) + "', '" + new String(t) + "', '" +  x + "', " + n + ")");

		double sum = 0;

		for (int j=0;j<t.length;j++)
		{
			//logger.debug("sumkp.t[" + j + "]=" + x + "' vs. " + x + "'");

			if (t[j] == x)
			{
				//logger.debug("sumk.t[" + j + "]='" + x + "'");
				sum += kp(s, prefix(t, j), n) * Math.pow(lambda, t.length - j + 1);
				//logger.debug("sumkp.sum[1.." + j + "]=" + sum);
			}
		}

		//logger.debug("sumkp.sum: " + sum);
		return sum;
	} // end sumkp

	//
	private char last(char[] t)
	{
		return t[t.length - 1];
	} // end last

	//
	private char[] prefix(char[] t)
	{
		return prefix(t, t.length - 1);
	} // end prefix

	//
	private char[] prefix(char[] s, int j)
	{
		//logger.debug("prefix: '" + new String(s) + "', " + j);

		if (j < 0)
			return null;

		char[] d = new char[j];

		for (int i=0;i<j;i++)
			d[i] = s[i];

		return d;
	} // end prefix

	//
	public static void main(String args[]) throws Exception
	{
		String logConfig = System.getProperty("log-config");
		if (logConfig == null)
			logConfig = "log-config.txt";

		PropertyConfigurator.configure(logConfig);

		if (args.length != 4)
		{
			System.err.println("java org.fbk.cit.hlt.dirha.kernel.CharKernel lambda length s t");
			System.exit(-1);
		}

		double lambda = Double.parseDouble(args[0]);
		int length = Integer.parseInt(args[1]);
		String s = args[2];
		String t = args[3];

		int min = Math.min(s.length(), t.length());
		if (min<length){
			length=min;
			logger.info("new length " + length);
		}

		CharKernel sk = new CharKernel(lambda, length);
		double k = sk.get(s, t);

		double kst = sk.get(s, t);
		double kss = sk.get(s, s);
		double ktt = sk.get(t, t);
		double knorm = kst / Math.sqrt(kss*ktt);

		logger.info("k('" + s + "', '" + t + "')=" + k);
		logger.info("k('" + s + "', '" + t + "')=" + knorm);
	} // end main

}
