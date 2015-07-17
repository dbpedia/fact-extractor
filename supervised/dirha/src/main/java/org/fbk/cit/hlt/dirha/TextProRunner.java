package org.fbk.cit.hlt.dirha;

import com.google.common.base.Joiner;
import org.apache.log4j.Logger;

import java.io.*;
import java.util.*;

/**
 * Created by admin on 4/21/15.
 */
public class TextProRunner {

    public static final Logger logger = Logger.getLogger(TextProRunner.class.getName());

    public static final List<String> TEXTPRO_CMD = Arrays.asList("perl", "textpro.pl", "-html", "-l", "ita", "-c", "token+sentence+pos+chunk");
    public static final String TEXTPRO_HOME = "/Users/admin/Apps/TextPro1.5.2_MacOSX/";

    public TextProRunner() {
    }


    public static void main(String[] args) {
        TextProRunner textProRunner = new TextProRunner();
        List<String> tokens = null;
        try {
            tokens = textProRunner.runTextPro("un esempio carino senza bestemmie!");
        } catch (IOException e) {
            e.printStackTrace();
        }
        System.out.println(textProRunner.extractNPChunks(tokens));
    }


    public List<String> runTextPro(String sentence) throws IOException {
        List<String> tokens = new ArrayList<>();
        ProcessBuilder pb = new ProcessBuilder(TEXTPRO_CMD);
        Map<String, String> env = pb.environment();
        env.put("TEXTPRO", TEXTPRO_HOME);
        pb.directory(new File(TEXTPRO_HOME));
        logger.debug(pb.environment());
        logger.debug(pb.command());
        pb.redirectErrorStream(true);
        Process p = pb.start();
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
        BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        writer.write(sentence + '\n');
        writer.close();
        while ((line = reader.readLine()) != null) {
            tokens.add(line);
        }
        assert pb.redirectInput() == ProcessBuilder.Redirect.PIPE;
        assert p.getInputStream().read() == -1;
        return tokens;
    }


    public Set<String> extractNPChunks(List<String> tokens) {
        Set<String> nps = new HashSet<>();
        List<List<String>> npTokens = new ArrayList<>();
        List<List<String>> tmp = new ArrayList<>();
        List<String> tmpChunk = new ArrayList<>();
        for (String tokenLine : tokens) {
            String[] parts = tokenLine.split("\t");
            String tag = parts[3];
            if (tag.matches("(B|I)\\-NP")) {
                String token = parts[0];
                if (tag.startsWith("B")) {
                    tmpChunk = new ArrayList<>();
                    tmpChunk.add(token);
                } else {
                    tmpChunk.add(token);
                }
                tmp.add(tmpChunk);
            }
        }
        for (List<String> chunk : tmp) {
          if (!npTokens.contains(chunk)) {
              npTokens.add(chunk);
          }
        }
        for (List<String> chunk : npTokens) {
            nps.add(Joiner.on(" ").skipNulls().join(chunk));
        }

        return nps;
    }
}
