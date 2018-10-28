def main():
    infile = open("student_files.csv" , "r")
    outfile = open("grade_report.txt" , "w")
    bin = []
    # Loop to take each line in file, and converts to reusable list of values
    for i in infile:
        dataline = i.replace('\r\n','').split(",")
        bin.append(dataline)
    # Loop to get each line of file and access the data in that line for our functions
    for i in range(1,len(bin)):
        print_name(bin[i])
        concerning(bin[i])
        troubling(bin[i])
    infile.close()
    outfile.close()

def print_name(bin):
    """Prints the name of student"""

    outfile = open("grade_report.txt" , "a")
    outfile.write("Student name: " + bin[1] + " " + bin[0] + "\n")
    outfile.close()

def concerning(bin):
    """This function detimines which student has concerning grades"""

    outfile = open("grade_report.txt" , "a")
    # Determiens if "Concerning Courses:" is relevant
    if bin[2] <= bin[4] and bin[2] > bin[3] or \
    bin[5] <= bin[7] and bin[5] > bin[6] or \
    bin[8] <= bin[10] and bin[8] > bin[9] or \
    bin[11] <= bin[13] and bin[11] > bin[12] or \
    bin[14] <= bin[16] and bin[14] > bin[15]:
        outfile.write("\t" + "Concerning Courses:" + "\n")
    if bin[2] <= bin[4] and bin[2] > bin[3]:
        outfile.write("\t" + "\t" + "Current Math grade: " + bin[2] + ", " + "Warning Math grade: " + bin[4] + "\n")
    if bin[5] <= bin[7] and bin[5] > bin[6]:
        outfile.write("\t" + "\t" + "Current English grade: " + bin[5] + ", " + "Warning English grade: " + bin[7] + "\n")
    if bin[8] <= bin[10] and bin[8] > bin[9]:
        outfile.write("\t" + "\t" + "Current History grade: " + bin[8] + ", " + "Warning History grade: " + bin[10] + "\n")
    if bin[11] <= bin[13] and bin[11] > bin[12]:
        outfile.write("\t" + "\t" + "Current Science grade: " + bin[11] + ", " + "Warning Science grade: " + bin[13] + "\n")
    if bin[14] <= bin[16] and bin[14] > bin[15]:
        outfile.write("\t" + "\t" + "Current Language grade: " + bin[14] + ", " + "Warning Language grade: " + bin[16] + "\n")
    outfile.close()

def troubling(bin):
    """This function detimines which student has troubling grades"""
    
    outfile = open("grade_report.txt" , "a")
    # Determiens if "Trouble Courses:" is relevant
    if bin[2] <= bin[3] or \
    bin[5] <= bin[6] or \
    bin[8] <= bin[9] or \
    bin[11] <= bin[12] or \
    bin[14] <= bin[15]:
        outfile.write("\t" + "Trouble Courses:" + "\n")
    if bin[2] <= bin[3]:
        outfile.write("\t" + "\t" + "Current Math grade: " + bin[2] + ", " + "Objective Math grade: " + bin[3] + "\n")
    if bin[5] <= bin[6]:
        outfile.write("\t" + "\t" + "Current English grade: " + bin[5] + ", " + "Objective English grade: " + bin[6] + "\n")
    if bin[8] <= bin[9]:
        outfile.write("\t" + "\t" + "Current History grade: " + bin[8] + ", " + "Objective History grade: " + bin[9] + "\n")
    if bin[11] <= bin[12]:
        outfile.write("\t" + "\t" + "Current Science grade: " + bin[11] + ", " + "Objective Science grade: " + bin[12] + "\n")
    if bin[14] <= bin[15]:
        outfile.write("\t" + "\t" + "Current Language grade: " + bin[14] + ", " + "Objective Language grade: " + bin[15] + "\n")
    outfile.close()

main()
