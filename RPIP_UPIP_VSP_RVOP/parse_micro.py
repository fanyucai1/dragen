# Email:yucai.fan@illumina.com
# 2014.07.19-2024.07.29
# version:1.0
# covlineages/pangolin:latest contains pangolin and snpEff
    # only anno Influenza A virus and Accession in virus_version
    # get covidseq pangolin information
# If species name does not match string(unable to type further), then output microorganisms
    # if consensusGenomeSequences + species['predictionInformation']['predictedPresent']=true,then output consensusGenomeSequences
    # if consensusGenomeSequences + species['predictionInformation']['predictedPresent']=true,then output vcf
    # vcf and fasta file named:re.sub(r'\s', "_", re.sub(r'[()]', "", species['name']))
# if proteinConsensusSequence + arm['predictionInformation']['predictedPresent']=true,then output proteinConsensusSequence
# if nucleotideConsensusSequence + arm['predictionInformation']['predictedPresent']=true,then output nucleotideConsensusSequence

import os,re
import subprocess,argparse
import time
import json

pangolin_snpeff="covlineages/pangolin:latest"
virus_version={'AY555152':'AY555152.3','AF084271':'AF084271.1',
               'CY163781':'CY163781.1','CY181523':'CY181523.1','CY163810':'CY163810.1','CY181515':'CY181515.1',
               'CY106613':'CY106613.1','CY115498':'CY115498.1','CY068784': 'CY068784.1','CY068787': 'CY068787.1',
               'CY017656':'CY017656.1', 'CY017672':'CY017672.1','CY116648':'CY116648.1',
               'EF619973':'EF619973.1',
               'HM114587':'HM114587.1',
               'KJ609205':'KJ609205.1','KJ609208':'KJ609208.1',
               'NC_026434':'NC_026434.1','NC_026437':'NC_026437.1',
               'KF280753':'KF280753.1','KF420298':'KF420298.1','KF280750':'KF280750.1','KF609513':'KF609513.1',
               'MN055357':'MN055357.1','MN055359':'MN055359.1',
               'MK495308':'MK495308.1','MK495311':'MK495311.1'
               }

parse=argparse.ArgumentParser("This script will parse dragen v4.3 VSPv2 json file.\n")
parse.add_argument("-j","--json",help="json file from dragen v4.3 VSPv2",required=True)
parse.add_argument("-o","--outdir",help="output directory",default=os.getcwd())
args=parse.parse_args()
args.json=os.path.abspath(args.json)
args.outdir=os.path.abspath(args.outdir)
if not os.path.exists(args.outdir):
    subprocess.check_output("mkdir -p %s"%args.outdir,shell=True)
start=time.time()
with open(args.json, "r") as load_f:
    load_dict = json.load(load_f)#dict
    prefix =load_dict['accession']
    out = os.path.abspath(args.outdir) + "/" + prefix
    ######################################## convert one line json to multiple lines
    new_dict=json.dumps(load_dict,indent=4, sort_keys=True)#str
    with open("%s_multiple_lines.json"%(out), "w") as outfile:
        outfile.write(new_dict)
    ########################################step1:sample quality control
    out1_file = open("%s.QC.Metrics.tsv" % out, "w")
    value_name = []
    # qcReport
    qcReport = load_dict['qcReport']

    ##sampleQc
    sampleQc = qcReport['sampleQc']
    key_name = ['totalRawReads','uniqueReads','uniqueReadsProportion', 'postQualityReads', 'postQualityReadsProportion','removedInDehostingReadsProportion', 'libraryQScore']
    cloumn_name = ['#QC Metrics\nTotal Raw Reads','Unique Reads','(%)Unique Reads Percentage', 'Post-Quality Reads', '(%)Post-Quality Reads Percentage', '(%)De-hosted Reads','library Q-Score']
    description = [
        'Number of reads in sample before read QC processing',
        'Number of unique reads in sample before read QC processing',
        'Percentage of unique reads in sample before read QC processing',
        'Number of reads in sample after read QC processing',
        'Percentage of post-quality reads in sample relative to total raw reads',
        'Percentage of host reads in sample removed relative to total raw reads',
        'Quality score of the library after read QC processing',
    ]
    for key in key_name:
        if re.search(r'Proportion$', key):
            sampleQc[key] = format(float(sampleQc[key]) * 100, ".2f")
        if re.search(r'Reads$', key):
            sampleQc[key] = format(int(sampleQc[key]), ",")
        value_name.append(sampleQc[key])

    ##enrichmentFactor
    enrichmentFactor = qcReport['enrichmentFactor']
    cloumn_name += ['Enrichment Factor']
    description += ['Enrichment factor value reflecting how well targeted regions were enriched']
    value_name.append(enrichmentFactor['value'])

    cloumn_name += ['Enrichment Category']
    value_name.append(enrichmentFactor['category'])
    description += ['Enrichment factor category: \'poor\', \'fair\', \'good\', or \'NC\' for not calculated']

    ##Sample_Composition
    sampleComposition = qcReport['sampleComposition']['readClassification']
    key_name = ['targetedMicrobial', 'untargeted', 'ambiguous', 'unclassified', 'lowComplexity',
                'targetedInternalControl']
    cloumn_name += ['#Sample Composition(%)\nTargeted Microbial', 'Untargeted', 'Ambiguous', 'Unclassified', 'Low Complexity',
                    'Targeted Internal Control']
    for key in key_name:
        value_name.append(format(float(sampleComposition[key]) * 100, ".2f"))
    description += ['Targeted microbial (non-IC) reference sequences',
                    'Untargeted reference sequences',
                    'More than one pathogen class',
                    'Could not be classified',
                    'Low complexity sequence',
                    'Targeted IC reference sequences'
                    ]

    ### target
    target=qcReport['sampleComposition']['targetedMicrobial']
    key_name=['viral','bacterial','fungal','parasitic','bacterialAmr']
    cloumn_name +=['#targetedMicrobial(%)\nviral','bacterial','fungal','parasitic','bacterialAmr']
    for key in key_name:
        value_name.append(format(float(target[key]) * 100, ".2f"))
    description += ['Viral targeted sequences',
                    'Bacterial targeted sequences',
                    'Fungal targeted sequences',
                    'Parasitic targeted sequences',
                    'Bacterial AMR targeted sequences']

    ### untarget
    un_target = qcReport['sampleComposition']['untargeted']
    key_name = ['viral', 'bacterial', 'fungal', 'parasitic', 'bacterialAmr','internalControl','human']
    cloumn_name+=['#untargeted(%)\nviral','bacterial','fungal','parasitic','bacterialAmr','internalControl','human']
    for key in key_name:
        value_name.append(format(float(un_target[key]) * 100, ".2f"))
    description+=['Viral untargeted sequences',
                  'Bacterial untargeted sequences',
                  'Fungal untargeted sequences',
                  'Parasitic untargeted sequences',
                  'Bacterial AMR untargeted sequences',
                  'Internal Control (IC) untargeted sequences',
                  'Human sequences']
    #output
    for i in range(0, len(cloumn_name)):
        out1_file.write(f"{cloumn_name[i]}\t{value_name[i]}\t{description[i]}\n")

    ### Internal Controls
    Internal_Controls = qcReport['internalControls']
    out1_file.write("#Internal Controls\n")
    for key in Internal_Controls:
        key['rpkm']=format(int(key['rpkm']), ",")
        out1_file.write(f"{key['name']}\t{key['rpkm']}\tRPKM for the {key['name']} control\n")
    out1_file.close()
    ########################################step2:Microorganisms
    out2_file = open("%s.microorganism.tsv" % out, "w")
    microorganisms = load_dict['targetReport']['microorganisms']  # 一个物种对应多个
    cloumn_name = ['Class','Microorganism', 'Present', 'Accessions', '% Coverage', '% ANI', 'Aligned Reads', 'Median Depth',
                   'RPKM', 'Absolute Quantity','Absolute Quantity(Formatted)','PhenotypicGroup','ASSOCIATED_AMR_MARKER_DETECTED','ASSOCIATED_AMR_MARKER_PREDICTED']

    key_name=['class','name','predictionInformation.predictedPresent','Accessions','coverage','ani','alignedReadCount','medianDepth',
              'rpkm','absoluteQuantityRatio','absoluteQuantityRatioFormatted','phenotypicGroup','associatedAmrMarkers.detected','associatedAmrMarkers.predicted']
    for i in range(0, len(cloumn_name)):
        if i == 0:
            out2_file.write("%s" % cloumn_name[i])
        else:
            out2_file.write("\t%s" % cloumn_name[i])
    for species in microorganisms:
        value_name = {}
        value_name['predictionInformation.predictedPresent'] = species['predictionInformation']['predictedPresent']
        accessions = ""
        if 'consensusGenomeSequences' in species and not re.search('unable to type further',species['name']) and species['predictionInformation']['predictedPresent']:  ###############output consensus sequences
            out3_file = open("%s.%s.fa" % (out,re.sub(r'\s', "_", re.sub(r'[()]', "", species['name']))), "w")
            for key in species['consensusGenomeSequences']:  # Consensus genome information. Included for RPIP viruses only.
                accessions += key['referenceAccession'] + ";"
                out3_file.write(">%s|reference:%s|description:%s|reference_length:%s|maximum_alignment_length:%s"
                                "|maximum_gap_length:%s|maximum_unaligned_length:%s"
                                "|coverage:%s|ani:%s|aligned_read_count:%s"
                                "|median_depth:%s\n%s\n"
                                % (species['name'], key['referenceAccession'], key['referenceDescription'],
                                   key['referenceLength'],key['maximumAlignmentLength'], key['maximumGapLength'],
                                   key['maximumUnalignedLength'],key['coverage'], key['ani'], key['alignedReadCount'], key['medianDepth'],key['sequence']))
            out3_file.close()
            #################################Extract Covidseq pangolin information
            if re.search('SARS-CoV-2', species['name']):
                cmd="docker run -v %s/:/tmp/ %s pangolin /tmp/%s.%s.fa --threads 4 --outfile /tmp/%s.%s.pangolin.results.csv"%(args.outdir,pangolin_snpeff,prefix,re.sub(r'\s', "_", re.sub(r'[()]', "", species['name'])),prefix,re.sub(r'\s', "_", re.sub(r'[()]', "", species['name'])))
                subprocess.call(cmd, shell=True)
        value_name['Accessions']=accessions.strip(";") # Accessions
        value_name['coverage']=format(float(species['coverage'] * 100), ".2f")# Coverage
        value_name['ani']=format(float(species['ani']) * 100, ".2f")  # ANI
        value_name['alignedReadCount']=format(int(species['alignedReadCount']), ",")  # Alinged Reads
        if 'associatedAmrMarkers' in species:
            value_name['associatedAmrMarkers.detected']=species['associatedAmrMarkers']['detected']
            value_name['associatedAmrMarkers.predicted']=species['associatedAmrMarkers']['predicted']
        else:
            value_name['associatedAmrMarkers.detected']=""
            value_name['associatedAmrMarkers.predicted']=""
        if not 'absoluteQuantityRatio' in species:
            value_name['absoluteQuantityRatio']=""
        if not 'absoluteQuantityRatioFormatted' in species:
            value_name['absoluteQuantityRatioFormatted'] = ""
        if not re.search('unable to type further',species['name']):
            for i in range(0, len(key_name)):
                if key_name[i] in species:
                    value_name[key_name[i]] =species[key_name[i]]
                if i == 0:
                    out2_file.write(f"\n{value_name[key_name[i]]}")
                else:
                    out2_file.write(f"\t{value_name[key_name[i]]}")
    ################################################################step3:The variants object is only present for select viruses
        if 'variants' in species and not re.search('unable to type further',species['name']) and species['predictionInformation']['predictedPresent']:
            out4_file = open("%s.%s.variants.vcf" % (out,re.sub(r'\s', "_", re.sub(r'[()]', "", species['name']))), "w")
            out4_file.write("##fileformat=VCFv4.2\n##source=DRAGEN Microbial Enrichment Plus\n"
                            "##INFO=<ID=AF,Number=1,Type=Float,Description=\"Allele Frequency\">\n"
                            "##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Read Depth\">\n"
                            "##INFO=<ID=SG,Number=1,Type=String,Description=\"Segment Name\">\n"
                            "##INFO=<ID=gene,Number=1,Type=String,Description=\"gene Name\">\n"
                            "##INFO=<ID=annotation,Number=1,Type=String,Description=\"Type of change (e.g. \"Nonsynonymous Variant\")\">\n"
                            "##INFO=<ID=product,Number=1,Type=String,Description=\"The protein product of the gene\">\n")
            out4_file.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
            snp=0
            for variant in species['variants']:
                if not 'segment' in variant:
                    variant['segment'] = "None"
                if variant['referenceAccession'] in virus_version:####check virus version
                    snp=1
                    out4_file.write("%s\t%s\t.\t%s\t%s\t.\tPASS\tAF=%s;DP=%s;SG=%s" % (virus_version[variant['referenceAccession']], variant['referencePosition'], variant['referenceAllele'],variant['variantAllele'],variant['alleleFrequency'], variant['depth'], variant['segment']))
                else:
                    out4_file.write("%s\t%s\t.\t%s\t%s\t.\tPASS\tAF=%s;DP=%s;SG=%s" % (variant['referenceAccession'], variant['referencePosition'], variant['referenceAllele'],variant['variantAllele'],variant['alleleFrequency'], variant['depth'], variant['segment']))
                if 'gene' in variant:
                    out4_file.write(f";gene={variant['gene']}")
                if 'annotation' in variant:
                    out4_file.write(f";annotation={variant['annotation']}")
                if 'product' in variant:
                    out4_file.write(f";product={variant['product']}")
                out4_file.write("\n")
            out4_file.close()
            ############################anno use snpeff only Influenza_A_virus
            if re.search('Influenza A virus', species['name']) and snp==1:
                cmd = ("docker run -v %s/:/database/ %s sh -c "
                       "\'java -Xmx64g -jar /software/snpEff/snpEff.jar "
                       "virus /database/%s.%s.variants.vcf >/database/%s.%s.anno.vcf\'")% (args.outdir, pangolin_snpeff, prefix, re.sub(r'\s', "_", re.sub(r'[()]', "", species['name'])), prefix, re.sub(r'\s', "_", re.sub(r'[()]', "", species['name'])))
                subprocess.check_call(cmd, shell=True)
    out2_file.close()
    ########################################step4:Antimicrobial Resistance Markers
    if len(load_dict['targetReport']['amrMarkers'])!=0:
        out6_file=open("%s.amrMarkers.tsv" % (out), "w")
        amrs = load_dict['targetReport']['amrMarkers']
        cloumn_name=['Class','name','predictionInformation.predictedPresent','predictionInformation.confidence','ncbiName','cardName','cardGeneFamily','cardModelType','Accession',
                     'coverage','rpkm','alignedReadCount','medianDepth','pid','associatedMicroorganisms.detected',
                     'associatedMicroorganisms.all','associatedMicroorganisms.predicted','ntChange','aaChange']
        for i in range(len(cloumn_name)):
            if i == 0:
                out6_file.write(f"{cloumn_name[i]}")
            else:
                out6_file.write(f"\t{cloumn_name[i]}")

        key_name=['class','name','predictionInformation.predictedPresent','predictionInformation.confidence','ncbiName','cardName','cardGeneFamily','cardModelType','referenceAccession',
                     'coverage','rpkm','alignedReadCount','medianDepth','pid','associatedMicroorganisms.detected',
                  'associatedMicroorganisms.all','associatedMicroorganisms.predicted','ntChange','aaChange']
        pro,nucl=0,0
        for arm in amrs:
            value_name,value_name['ntChange'],value_name['aaChange'] ={},[],[]
            if 'variants' in arm:
                for tmp in arm['variants']:
                    if 'aaChange' in tmp:
                        value_name['aaChange'].append(tmp['aaChange'])
                    if 'ntChange' in tmp:
                        value_name['ntChange'].append(tmp['ntChange'])
            value_name['associatedMicroorganisms.detected'] =arm['associatedMicroorganisms']['detected']
            value_name['associatedMicroorganisms.all'] = arm['associatedMicroorganisms']['all']
            value_name['associatedMicroorganisms.predicted']=arm['associatedMicroorganisms']['predicted']
            value_name['predictionInformation.predictedPresent'] = arm['predictionInformation']['predictedPresent']
            value_name['predictionInformation.confidence'] =arm['predictionInformation']['confidence']
            for i in range(0, len(key_name)):
                if key_name[i] in arm:
                    value_name[key_name[i]] = arm[key_name[i]]
                if i==0:
                    out6_file.write(f"\n{value_name[key_name[i]]}")
                else:
                    out6_file.write(f"\t{value_name[key_name[i]]}")
            if 'proteinConsensusSequence' in arm and arm['predictionInformation']['predictedPresent']:
                pro+=1
                seqid = ">%s|reference:%s" % (arm['name'], arm['referenceAccession'])
                if pro==1:
                    out7_file = open("%s_amr_protein_consensus.fa" % (out), "w")
                else:
                    out7_file = open("%s_amr_protein_consensus.fa" % (out), "a+")
                protein = arm['proteinConsensusSequence']
                out7_file.write("%s\n%s\n" % (seqid, protein))
                out7_file.close()
            if 'nucleotideConsensusSequence' in arm and arm['predictionInformation']['predictedPresent']:
                nucl+=1
                seqid = ">%s|reference:%s" % (arm['name'], arm['referenceAccession'])
                if nucl==1:
                    out8_file = open("%s_amr_nucleotide_consensus.fa" % (out), "w")
                else:
                    out8_file = open("%s_amr_nucleotide_consensus.fa" % (out), "a+")
                nucleotide = arm['nucleotideConsensusSequence']
                out8_file.write("%s\n%s\n" % (seqid, nucleotide))
                out8_file.close()
        out6_file.close()
end = time.time()
print("Elapse time %s seconds" % (end - start))