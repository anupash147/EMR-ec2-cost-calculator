# EMR-ec2-cost-calculator
This project is written in python. It calculates the EMR cluster cost by getting the spot and ondemand prices of the instances and adding up the emr charges.

# Requires
python3
pip

# How to use it ?
* step 1 git clone the project
    > git clone https://github.com/anupash147/EMR-ec2-cost-calculator.git
* Installing necessary softwares with pip
    > cd EMR-ec2-cost-calculator

    > sudo pip install -r requirements.txt
* export your aws credentials
* run the python module.
### Examples
    > python calculate_emr_cost.py -c j-XXXXXXXXXX
or

    > python calculate_emr_cost.py --cluster-id j-EIN8JALVZ26Q

#### Result
'''
your clusterid - j-xxxxxx in region us-east-1                                                                             
=======CORE=======                                                                                                                  
Ec2 cost: $0.35 per/hr and EMR cost $0.088 per/hr                                                                                   
ID: ig-xxxxxxxx  Machine Type:m1.xlarge  Market : ON_DEMAND  Charged @0.438                                                     
Total instances used : 184                                                                                                          
Cost for this task group is $3627.516     

=======MASTER=======                                                                                                                
Ec2 cost: $5.52 per/hr and EMR cost $0.27 per/hr                                                                                    
ID: ig-xxxxxxxx  Machine Type:d2.8xlarge  Market : ON_DEMAND  Charged @5.79                                                    
Total instances used : 1                                                                                                            
Cost for this task group is $266.34                                                                                                 
Total cost of the EMR ``$3893.856  ``                                                                                                   
=========================                                                                               
