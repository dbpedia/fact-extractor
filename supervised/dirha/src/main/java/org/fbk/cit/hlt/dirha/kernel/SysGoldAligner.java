package org.fbk.cit.hlt.dirha.kernel;

import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.File;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * User: giuliano
 * Date: 2/4/13
 * Time: 10:16 AM
 * To change this template use File | Settings | File Templates.
 */
public class SysGoldAligner {
	/**
	 * Define a static logger variable so that it references the
	 * Logger instance named <code>SysGoldAligner</code>.
	 */
	static Logger logger = Logger.getLogger(SysGoldAligner.class.getName());

	int tp = 0, fp = 0, fn = 0;

	double precision = 0, recall = 0, f1 = 0;

	private static DecimalFormat df = new DecimalFormat("##0.0000");

	public SysGoldAligner(File sys, File gold) throws IOException {
		GoldReader goldReader = new GoldReader(gold);
		List<Sentence> goldGentenceList = goldReader.getSentenceList();

		SystemReader systemReader = new SystemReader(sys);
		List<Sentence> systemSentenceList = systemReader.getSentenceList();
		align(systemSentenceList, goldGentenceList);
	}

	void align(List<Sentence> systemSentenceList, List<Sentence> goldGentenceList) {
		//CharKernel charKernel = new CharKernel(1, 3);
		StringKernel stringKernel = new StringKernel(1, 2);
		logger.debug(systemSentenceList.size() + " vs " + goldGentenceList.size());
		int tot = 0;
		int correctFrame = 0;
		int correctRole = 0;
		for (int i = 0; i < systemSentenceList.size(); i++) {
			String sys = systemSentenceList.get(i).toString().toLowerCase();
			double max = 0;
			int jMax = 0;

			for (int j = 0; j < goldGentenceList.size(); j++) {
				String gold = goldGentenceList.get(j).toString().toLowerCase();
				//double d = charKernel.get(sys, gold);
				double d = stringKernel.get(sys, gold);
				if (d > max) {
					max = d;
					jMax = j;
				}
				//logger.debug(d);

			}

			logger.debug(i + "\t" + systemSentenceList.get(i));
			logger.debug(jMax + "\t" + goldGentenceList.get(jMax));
			logger.debug(max);
			logger.debug("");
			correctFrame += checkFrame(systemSentenceList.get(i).getFrameList(), goldGentenceList.get(jMax).getFrameList());
			checkFrameAndRole(systemSentenceList.get(i).getFrameList(), goldGentenceList.get(jMax).getFrameList());

			tot++;
		}

		logger.info(correctFrame + "\t" + tot + "\t" + (double) correctFrame / tot);
		precision = (double) tp / (tp + fp);
		recall = (double) tp / (tp + fn);
		f1 = (2 * precision * recall) / (precision + recall);
		logger.info(tp + "\t" + fp + "\t" + fn + "\t" + df.format(precision) + "\t" +  df.format(recall) + "\t" +  df.format(f1));

	}

	int checkFrame(List<Frame> systemFrameList, List<Frame> goldFrameList)
	{
		for (int i = 0; i < systemFrameList.size(); i++) {
			Frame systemFrame = systemFrameList.get(i);
			for (int j = 0; j < goldFrameList.size(); j++) {
				Frame goldFrame = goldFrameList.get(j);
				//if (systemFrame.equals(goldFrame))
				if (systemFrame.getName().equals(goldFrame.getName()))
				{
					logger.info("<<<" + systemFrame + " == "+ goldFrame + ">>>");
					
					return 1;
				}
			}
		}
		return 0;
	}

	void checkFrameAndRole(List<Frame> systemFrameList, List<Frame> goldFrameList)
	{

		for (int i = 0; i < systemFrameList.size(); i++) {
			Frame systemFrame = systemFrameList.get(i);
			for (int j = 0; j < goldFrameList.size(); j++) {
				Frame goldFrame = goldFrameList.get(j);
				//if (systemFrame.equals(goldFrame))
				//todo: compare also the target
				if (systemFrame.getName().equals(goldFrame.getName()))
				{
					logger.info("<<<" + systemFrame + " == "+ goldFrame + ">>>");
					checkRole(systemFrame.getRoleList(), goldFrame.getRoleList());

				}
			}
		}
	}

	void checkRole(List<Role> systemRoleList, List<Role> goldRoleList)
	{
		int tp = 0, fp = 0, fn = 0;
		for (int i = 0; i < systemRoleList.size(); i++) {
			Role systemRole = systemRoleList.get(i);
			for (int j = 0; j < goldRoleList.size(); j++) {
				Role goldRole = goldRoleList.get(j);
				//todo: compare also the arg
				if (systemRole.getName().equals(goldRole.getName()) && systemRole.getArg().equalsIgnoreCase(goldRole.getArg()))
				{
					logger.info("{{{" + systemRole + " == "+ goldRole + "}}}");
					tp++;
				}
			}
		}
		fp = systemRoleList.size() - tp;
		fn = goldRoleList.size() - tp;
		logger.debug(tp + "\t" + fp + "\t" + fn);
		this.tp += tp;
		this.fp += fp;
		this.fn += fn;
		logger.info(this.tp + "\t" + this.fp + "\t" + this.fn);
	}

	public static void main(String[] args) throws Exception {
		// java com.ml.test.net.HttpServerDemo
		String logConfig = System.getProperty("log-config");
		if (logConfig == null) { logConfig = "log-config.txt"; }

		PropertyConfigurator.configure(logConfig);

		SysGoldAligner sysGoldAligner = new SysGoldAligner(new File(args[0]), new File(args[1]));

	}
}
