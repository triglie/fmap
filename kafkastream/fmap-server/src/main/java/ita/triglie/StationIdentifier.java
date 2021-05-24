package ita.triglie;

public class StationIdentifier {
    private String PI;
    private String province;
    private Float FM;

    public StationIdentifier(Float FM, String province) {
        this.FM = FM;
        this.province = province;
        this.PI = null;
    }

    public StationIdentifier(Float FM, String province, String PI) {
        this.FM = FM;
        this.province = province;
        this.PI = PI;
    }

    public String getPI() {
        return PI;
    }

    public void setPI(String PI) {
        this.PI = PI;
    }

    public Float getFM() {
        return FM;
    }

    public void setFM(Float FM) {
        this.FM = FM;
    }

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public boolean hasProgrammeIdentifier() {
        return this.PI != null;
    }
}
