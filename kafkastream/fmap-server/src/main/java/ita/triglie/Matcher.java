package ita.triglie;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public abstract class Matcher {

    protected List<String> radioNames;
    protected List<Float> listFM;
    protected List<String> listPI;

    public Matcher() {
        radioNames = new ArrayList<>();
        listFM = new ArrayList<>();
        listPI = new ArrayList<>();
    }

    public String match(StationIdentifier identifier) {
        Float[] castedFMArray = listFM.stream().toArray(Float[]::new);
        Float closestFrequence = FindClosest.findClosest(castedFMArray, identifier.getFM());
        return radioNames.get(listFM.indexOf(closestFrequence));
    }

    abstract protected void loadInfo(String filename);

    protected String createStringCSV(String filename) {
        BufferedReader inputCSV;
        StringBuilder csv = new StringBuilder();
        try {
            inputCSV = new BufferedReader(new FileReader(filename));
            String line = inputCSV.readLine();
            while((line = inputCSV.readLine()) != null) {
                csv.append(line + "\n");
            }
            inputCSV.close();

        } catch (IOException e) {
            e.printStackTrace();
            System.exit(-1);
        }
        return csv.toString();
    }
}
