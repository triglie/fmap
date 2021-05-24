package ita.triglie;

import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;

public class NationalMatcher extends Matcher {

    private String filename = "Resources/complete-pi-station-map.csv";

    public NationalMatcher() {
        super();
        loadInfo(filename);
    }

    @Override
    public String match(StationIdentifier identifier) {
        if (!identifier.hasProgrammeIdentifier()) {
            return super.match(identifier);
        }
        int stationIndex = super.listPI.indexOf(identifier.getPI());
        if (stationIndex < 0) {
            return super.match(identifier);
        }
        return super.radioNames.get(stationIndex);
    }

    @Override
    protected void loadInfo(String filename) {
        String csv = super.createStringCSV(filename);
        Reader in = new StringReader(csv.toString());
        try {
            for (CSVRecord record : CSVFormat.DEFAULT.parse(in)) {
                int i = 0;
                for (String field : record) {
                    switch(i++) {
                        case 0: {super.radioNames.add(field); break;}
                        case 1: {super.listFM.add(Float.parseFloat(field)); break;}
                        case 2: {super.listPI.add(field); break;}
                    }
                }
            }
        } catch (IOException e) {
            System.exit(-1);
            e.printStackTrace();
        }
    }

}