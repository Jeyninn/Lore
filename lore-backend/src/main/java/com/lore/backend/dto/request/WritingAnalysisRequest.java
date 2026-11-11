
package com.lore.backend.dto.request;

public class WritingAnalysisRequest {

    private String writingSample;
    private boolean consentToAnalyzeWriting;

    public String getWritingSample() {
        return writingSample;
    }

    public void setWritingSample(String writingSample) {
        this.writingSample = writingSample;
    }

    public boolean isConsentToAnalyzeWriting() {
        return consentToAnalyzeWriting;
    }

    public void setConsentToAnalyzeWriting(boolean consentToAnalyzeWriting) {
        this.consentToAnalyzeWriting = consentToAnalyzeWriting;
    }
}
